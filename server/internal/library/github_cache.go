package library

import (
	"crypto/rand"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"time"
)

// parserVersion marks cache files produced by the tolerant chapter-name parser.
const parserVersion = 1

var (
	repoNameRe = regexp.MustCompile(`^[A-Za-z0-9._-]{1,100}$`)
	shaRe      = regexp.MustCompile(`^[0-9a-f]{40}([0-9a-f]{24})?$`)
)

// AtomicWrite writes data to a temp file in the same directory and renames it
// over path, so readers never see a partial file.
func AtomicWrite(path string, data []byte) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	var rnd [6]byte
	rand.Read(rnd[:])
	tmp := fmt.Sprintf("%s.%d%s.tmp", path, os.Getpid(), hex.EncodeToString(rnd[:]))
	f, err := os.OpenFile(tmp, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
	if err != nil {
		return err
	}
	_, err = f.Write(data)
	if cerr := f.Close(); err == nil {
		err = cerr
	}
	if err == nil {
		// on Windows the target may be briefly open in another process
		for i := 0; i < 5; i++ {
			if err = os.Rename(tmp, path); err == nil {
				return nil
			}
			time.Sleep(time.Duration(20*(i+1)) * time.Millisecond)
		}
	}
	os.Remove(tmp)
	return err
}

type ghFile struct{ file, sha string }

// ghStory is one story folder of a repo tree.
type ghStory struct {
	info      string // blob sha of info.json or ""
	coverFile string
	coverSha  string
	files     []ghFile // every chapter-named file
}

func (s *ghStory) names() []string {
	out := make([]string, len(s.files))
	for i, f := range s.files {
		out[i] = f.file
	}
	return out
}

func (s *ghStory) sha(file string) (string, bool) {
	for _, f := range s.files {
		if f.file == file {
			return f.sha, true
		}
	}
	return "", false
}

// ghTree is the parsed tree of one repo.
type ghTree struct {
	sha     string
	marked  bool // written by this parser version
	stories map[string]*ghStory
	used    time.Time
}

type diskStory struct {
	Info     *string    `json:"info"`
	Chapters [][4]any   `json:"chapters"`
	Cover    *[2]string `json:"cover"`
}

type diskTree struct {
	V       int                   `json:"v"`
	P       int                   `json:"p,omitempty"`
	Sha     string                `json:"sha"`
	Stories map[string]*diskStory `json:"stories"`
}

func treePath(dir, repo string) string { return filepath.Join(dir, "tree_"+repo+".json") }
func sumPath(dir, repo string) string  { return filepath.Join(dir, "sum_"+repo+".json") }

// loadTreeFile reads a tree cache file; any defect is a cache miss (nil).
func loadTreeFile(dir, repo string) *ghTree {
	b, err := os.ReadFile(treePath(dir, repo))
	if err != nil {
		return nil
	}
	var d diskTree
	if json.Unmarshal(b, &d) != nil || d.V != 2 || d.Stories == nil || d.Sha == "" {
		return nil
	}
	t := &ghTree{sha: d.Sha, marked: d.P >= parserVersion, stories: make(map[string]*ghStory, len(d.Stories))}
	for name, ds := range d.Stories {
		if ds == nil || name == "" {
			continue
		}
		st := &ghStory{}
		if ds.Info != nil && shaRe.MatchString(*ds.Info) {
			st.info = *ds.Info
		}
		if ds.Cover != nil && shaRe.MatchString(ds.Cover[1]) && IsImageName(ds.Cover[0]) {
			st.coverFile, st.coverSha = ds.Cover[0], ds.Cover[1]
		}
		st.files = make([]ghFile, 0, len(ds.Chapters))
		for _, c := range ds.Chapters {
			file, ok1 := c[2].(string)
			sha, ok2 := c[3].(string)
			if !ok1 || !ok2 || !shaRe.MatchString(sha) {
				continue
			}
			if _, ok := ParseChapterName(file); ok {
				st.files = append(st.files, ghFile{file, sha})
			}
		}
		t.stories[name] = st
	}
	return t
}

// saveTreeFile writes the tree in the layout the old server also understands.
func saveTreeFile(dir, repo string, t *ghTree) error {
	d := diskTree{V: 2, P: parserVersion, Sha: t.sha, Stories: make(map[string]*diskStory, len(t.stories))}
	for name, st := range t.stories {
		ds := &diskStory{Chapters: make([][4]any, 0, len(st.files))}
		if st.info != "" {
			s := st.info
			ds.Info = &s
		}
		if st.coverSha != "" {
			ds.Cover = &[2]string{st.coverFile, st.coverSha}
		}
		type row struct {
			p ChapterName
			f ghFile
		}
		rows := make([]row, 0, len(st.files))
		for _, f := range st.files {
			if p, ok := ParseChapterName(f.file); ok {
				rows = append(rows, row{p, f})
			}
		}
		sort.Slice(rows, func(i, j int) bool {
			a, b := rows[i], rows[j]
			switch {
			case a.p.Vol != b.p.Vol:
				return a.p.Vol < b.p.Vol
			case a.p.N != b.p.N:
				return a.p.N < b.p.N
			case a.p.Sub != b.p.Sub:
				return a.p.Sub < b.p.Sub
			}
			return a.f.file < b.f.file
		})
		for _, r := range rows {
			ds.Chapters = append(ds.Chapters, [4]any{r.p.N, r.p.Title, r.f.file, r.f.sha})
		}
		d.Stories[name] = ds
	}
	b, err := marshalNoEscape(d)
	if err != nil {
		return err
	}
	return AtomicWrite(treePath(dir, repo), b)
}

// sumStory is the compact per-story record kept for every repo.
type sumStory struct {
	Story string       `json:"story"`
	Info  string       `json:"info,omitempty"`
	N     int          `json:"n"`
	Img   bool         `json:"img,omitempty"`
	Sum   *diskSummary `json:"sum,omitempty"` // parsed info.json, once known
}

type diskSummary struct {
	Summary
	Updated string `json:"updated,omitempty"`
}

// repoSum is the small summary of one repo (enough to list its stories).
type repoSum struct {
	P       int        `json:"p"`
	Sha     string     `json:"sha"`
	Pushed  string     `json:"pushed,omitempty"`
	Stories []sumStory `json:"stories"`

	at    time.Time // when the head was last confirmed
	stale bool
}

func sumFromTree(t *ghTree) *repoSum {
	s := &repoSum{P: parserVersion, Sha: t.sha, Stories: make([]sumStory, 0, len(t.stories))}
	for name, st := range t.stories {
		s.Stories = append(s.Stories, sumStory{Story: name, Info: st.info, N: len(ChapterList(st.names())), Img: st.coverSha != ""})
	}
	SortVi(s.Stories, func(x sumStory) string { return x.Story })
	return s
}

func loadSumFile(dir, repo string) *repoSum {
	b, err := os.ReadFile(sumPath(dir, repo))
	if err != nil {
		return nil
	}
	var s repoSum
	if json.Unmarshal(b, &s) != nil || s.P != parserVersion || s.Sha == "" {
		return nil
	}
	for i := range s.Stories {
		st := &s.Stories[i]
		if st.Story == "" || (st.Info != "" && !shaRe.MatchString(st.Info)) {
			return nil
		}
		if st.Sum != nil {
			st.Sum.Summary.Updated = st.Sum.Updated
			if st.Sum.Genres == nil {
				st.Sum.Genres = []string{}
			}
			if st.Sum.Tags == nil {
				st.Sum.Tags = []string{}
			}
		}
	}
	return &s
}

func saveSumFile(dir, repo string, s *repoSum) error {
	b, err := marshalNoEscape(s)
	if err != nil {
		return err
	}
	return AtomicWrite(sumPath(dir, repo), b)
}

type diskRepos struct {
	Owner  string `json:"owner"`
	Prefix string `json:"prefix"`
	At     int64  `json:"at"`
	Repos  []Repo `json:"repos"`
}

func reposPath(dir, owner, prefix string) string {
	h := sha1.Sum([]byte(owner + "|" + prefix))
	return filepath.Join(dir, "repos_"+hex.EncodeToString(h[:])[:12]+".json")
}

func blobPath(dir, sha string) string { return filepath.Join(dir, "blobs", sha[:2], sha) }

// gitBlobOK verifies data against a SHA-1 git blob id (SHA-256 ids are not checked).
func gitBlobOK(sha string, data []byte) bool {
	if len(sha) != 40 {
		return true
	}
	h := sha1.New()
	fmt.Fprintf(h, "blob %d\x00", len(data))
	h.Write(data)
	return hex.EncodeToString(h.Sum(nil)) == sha
}
