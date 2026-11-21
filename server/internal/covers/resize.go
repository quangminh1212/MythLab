package covers

import (
	"bytes"
	"context"
	"errors"
	"image"
	"image/color"
	"image/draw"
	_ "image/gif" // decoders
	"image/jpeg"
	_ "image/png"
	"os"
	"path/filepath"
	"strconv"

	xdraw "golang.org/x/image/draw"
	_ "golang.org/x/image/webp"

	"mythlab/internal/library"
)

// Widths are the accepted values of the cover `w` parameter.
var Widths = map[int]bool{160: true, 240: true, 320: true, 480: true}

const (
	maxPixels   = 40 << 20 // decoded size guard
	jpegQuality = 82
)

// ErrNoResize means the source should be served as it is: it cannot be
// decoded here (AVIF), is too large to decode safely, or is already small.
var ErrNoResize = errors.New("serve original")

// Resize scales src down to width w and encodes it as JPEG.
func Resize(src []byte, w int) ([]byte, error) {
	cfg, _, err := image.DecodeConfig(bytes.NewReader(src))
	if err != nil || cfg.Width <= 0 || cfg.Height <= 0 || int64(cfg.Width)*int64(cfg.Height) > maxPixels {
		return nil, ErrNoResize
	}
	if cfg.Width <= w {
		return nil, ErrNoResize // never upscale
	}
	img, _, err := image.Decode(bytes.NewReader(src))
	if err != nil {
		return nil, ErrNoResize
	}
	b := img.Bounds()
	h := int(int64(b.Dy()) * int64(w) / int64(b.Dx()))
	if h < 1 {
		h = 1
	}
	dst := image.NewRGBA(image.Rect(0, 0, w, h))
	draw.Draw(dst, dst.Bounds(), image.NewUniform(color.White), image.Point{}, draw.Src) // flatten transparency
	xdraw.CatmullRom.Scale(dst, dst.Bounds(), img, b, xdraw.Over, nil)
	var out bytes.Buffer
	if err := jpeg.Encode(&out, dst, &jpeg.Options{Quality: jpegQuality}); err != nil {
		return nil, ErrNoResize
	}
	return out.Bytes(), nil
}

// Resized returns the path of the cached w-wide JPEG of an image. tag
// identifies the source version (it changes when the image changes); load
// supplies the source bytes on a cache miss. ErrNoResize = use the original.
func (s *Store) Resized(ctx context.Context, tag string, w int, load func() ([]byte, error)) (string, error) {
	if !Widths[w] || tag == "" {
		return "", ErrNoResize
	}
	name := Key(tag) + "_" + strconv.Itoa(w)
	file := filepath.Join(s.dir, "r", name+".jpg")
	none := filepath.Join(s.dir, "r", name+".none") // remembered "serve original"
	if st, err := os.Stat(file); err == nil && st.Size() > 0 {
		return file, nil
	}
	if _, err := os.Stat(none); err == nil {
		return "", ErrNoResize
	}
	ch := s.sf.DoChan("r:"+name, func() (any, error) {
		if st, err := os.Stat(file); err == nil && st.Size() > 0 {
			return file, nil
		}
		s.sem <- struct{}{}
		defer func() { <-s.sem }()
		src, err := load()
		if err != nil {
			return nil, err
		}
		out, err := Resize(src, w)
		if err != nil {
			library.AtomicWrite(none, []byte("-"))
			return nil, err
		}
		if err := library.AtomicWrite(file, out); err != nil {
			s.logf("[covers] không ghi được ảnh thu nhỏ: %v", err)
			return nil, ErrNoResize
		}
		return file, nil
	})
	select {
	case r := <-ch:
		if r.Err != nil {
			return "", r.Err
		}
		return r.Val.(string), nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}
