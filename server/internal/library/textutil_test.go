package library

import (
	"encoding/json"
	"os"
	"reflect"
	"strings"
	"testing"
)

type fixture struct {
	ParseChapterName []struct {
		File   string `json:"file"`
		Expect *struct {
			N     int64  `json:"n"`
			Title string `json:"title"`
			Sub   int64  `json:"sub"`
			Vol   int64  `json:"vol"`
		} `json:"expect"`
	} `json:"parseChapterName"`
	ChapterList []struct {
		Note   string    `json:"note"`
		Files  []string  `json:"files"`
		Expect []Chapter `json:"expect"`
	} `json:"chapterList"`
	CleanChapterText []struct {
		Note   string `json:"note"`
		Text   string `json:"text"`
		N      *int64 `json:"n"`
		Expect struct {
			Title      *string  `json:"title"`
			Paragraphs []string `json:"paragraphs"`
		} `json:"expect"`
	} `json:"cleanChapterText"`
	ChapterJSON []struct {
		Text   string      `json:"text"`
		File   string      `json:"file"`
		Expect ChapterJSON `json:"expect"`
	} `json:"chapterJson"`
	NormTxt []struct {
		In  string `json:"in"`
		Out string `json:"out"`
	} `json:"normTxt"`
	NormKey []struct {
		In  string `json:"in"`
		Out string `json:"out"`
	} `json:"normKey"`
	SearchMatch []struct {
		Q     string `json:"q"`
		Field string `json:"field"`
		Match bool   `json:"match"`
	} `json:"searchMatch"`
	InfoSummary []struct {
		Info     json.RawMessage `json:"info"`
		Fallback string          `json:"fallback"`
		Expect   json.RawMessage `json:"expect"`
	} `json:"infoSummary"`
	PickCover []struct {
		Names  []string `json:"names"`
		Expect *string  `json:"expect"`
	} `json:"pickCover"`
}

func loadFixture(t *testing.T) fixture {
	t.Helper()
	b, err := os.ReadFile("testdata/textutil_cases.json")
	if err != nil {
		t.Fatal(err)
	}
	var f fixture
	if err := json.Unmarshal(b, &f); err != nil {
		t.Fatal(err)
	}
	if len(f.ParseChapterName) == 0 || len(f.ChapterList) == 0 || len(f.CleanChapterText) == 0 ||
		len(f.ChapterJSON) == 0 || len(f.NormTxt) == 0 || len(f.NormKey) == 0 || len(f.SearchMatch) == 0 ||
		len(f.InfoSummary) == 0 || len(f.PickCover) == 0 {
		t.Fatal("fixture section missing")
	}
	return f
}

func TestFixtureParseChapterName(t *testing.T) {
	for _, c := range loadFixture(t).ParseChapterName {
		p, ok := ParseChapterName(c.File)
		if c.Expect == nil {
			if ok {
				t.Errorf("%q: expected no match, got %+v", c.File, p)
			}
			continue
		}
		if !ok || p.N != c.Expect.N || p.Title != c.Expect.Title || p.Sub != c.Expect.Sub || p.Vol != c.Expect.Vol {
			t.Errorf("%q: got ok=%v %+v, want %+v", c.File, ok, p, *c.Expect)
		}
	}
}

func TestFixtureChapterList(t *testing.T) {
	for _, c := range loadFixture(t).ChapterList {
		if got := ChapterList(c.Files); !reflect.DeepEqual(got, c.Expect) {
			t.Errorf("%s:\n got %+v\nwant %+v", c.Note, got, c.Expect)
		}
	}
}

func TestFixtureCleanChapterText(t *testing.T) {
	for _, c := range loadFixture(t).CleanChapterText {
		var n int64
		if c.N != nil {
			n = *c.N
		}
		title, has, paras := CleanChapterText(c.Text, n, c.N != nil)
		if (c.Expect.Title == nil) != !has || (has && title != *c.Expect.Title) {
			t.Errorf("%s: title %q/%v", c.Note, title, has)
		}
		if !reflect.DeepEqual(paras, c.Expect.Paragraphs) {
			t.Errorf("%s: paragraphs %q want %q", c.Note, paras, c.Expect.Paragraphs)
		}
	}
}

func TestFixtureChapterJSON(t *testing.T) {
	for _, c := range loadFixture(t).ChapterJSON {
		got, _ := json.Marshal(BuildChapterJSON(c.Text, c.File))
		want, _ := json.Marshal(c.Expect)
		if string(got) != string(want) {
			t.Errorf("%s:\n got %s\nwant %s", c.File, got, want)
		}
	}
}

func TestFixtureNorm(t *testing.T) {
	f := loadFixture(t)
	for _, c := range f.NormTxt {
		if got := NormTxt(c.In); got != c.Out {
			t.Errorf("NormTxt(%q)=%q want %q", c.In, got, c.Out)
		}
	}
	for _, c := range f.NormKey {
		if got := NormKey(c.In); got != c.Out {
			t.Errorf("NormKey(%q)=%q want %q", c.In, got, c.Out)
		}
	}
	for _, c := range f.SearchMatch {
		if got := SearchMatch(c.Q, c.Field); got != c.Match {
			t.Errorf("SearchMatch(%q,%q)=%v", c.Q, c.Field, got)
		}
	}
}

func TestFixtureInfoSummary(t *testing.T) {
	for i, c := range loadFixture(t).InfoSummary {
		got, _ := json.Marshal(InfoSummary(c.Info, c.Fallback))
		var a, b any
		_ = json.Unmarshal(got, &a)
		_ = json.Unmarshal(c.Expect, &b)
		if !reflect.DeepEqual(a, b) {
			t.Errorf("case %d:\n got %s\nwant %s", i, got, c.Expect)
		}
	}
}

func TestFixturePickCover(t *testing.T) {
	for _, c := range loadFixture(t).PickCover {
		got := PickCover(c.Names)
		want := ""
		if c.Expect != nil {
			want = *c.Expect
		}
		if got != want {
			t.Errorf("PickCover(%q)=%q want %q", c.Names, got, want)
		}
	}
}

func TestDecodeText(t *testing.T) {
	if got := DecodeText([]byte("\xef\xbb\xbfa\xffb")); got != "a\ufffdb" {
		t.Errorf("utf8: %q", got)
	}
	if got := DecodeText([]byte{0xff, 0xfe, 'h', 0, 0xb0, 0x01}); got != "hư" {
		t.Errorf("utf16le: %q", got)
	}
	if got := DecodeText([]byte{0xfe, 0xff, 0, 'h'}); got != "h" {
		t.Errorf("utf16be: %q", got)
	}
}

// One rule above the heading and the closing rule far below (seen in the
// manuscript): the heading is still the title, not the first paragraph.
func TestCleanChapterTextLoneRuleAboveTitle(t *testing.T) {
	rule := strings.Repeat("=", 60)
	text := rule + "\r\nChương 341: Lễ bàn giao\r\n\r\na\r\nb\r\nc\r\nd\r\ne\r\nf\r\ng\r\n" + rule + "\r\n" + rule + "\r\n\r\nNội dung.\r\n"
	title, has, paras := CleanChapterText(text, 341, true)
	want := []string{"a", "b", "c", "d", "e", "f", "g", SceneBreak, "Nội dung."}
	if !has || title != "Chương 341: Lễ bàn giao" || !reflect.DeepEqual(paras, want) {
		t.Fatalf("title %q %v paras %q", title, has, paras)
	}
}
