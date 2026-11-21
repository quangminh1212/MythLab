package edgetts

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
)

// Voice is one entry of the service's voice list.
type Voice struct {
	ShortName, Locale, Gender, FriendlyName string
}

// maxVoicesBody bounds the voice list download (the real list is ~200 kB).
const maxVoicesBody = 8 << 20

// Voices returns every voice the service offers. The list is cached for
// Options.VoicesTTL; when a refresh fails and an older list exists, the older
// list is returned without error. The returned slice is the caller's.
func (c *Client) Voices(ctx context.Context) ([]Voice, error) {
	if vs, fresh := c.cachedVoices(); fresh {
		return vs, nil
	}

	// One download at a time; the others wait and then reuse its result.
	select {
	case c.voicesFetch <- struct{}{}:
	case <-ctx.Done():
		return nil, ctx.Err()
	}
	defer func() { <-c.voicesFetch }()
	if vs, fresh := c.cachedVoices(); fresh {
		return vs, nil
	}

	vs, err := c.fetchVoices(ctx)
	if isForbidden(err) {
		vs, err = c.fetchVoices(ctx)
	}
	if err != nil {
		if stale, _ := c.cachedVoices(); stale != nil && ctx.Err() == nil {
			return stale, nil
		}
		return nil, err
	}

	c.mu.Lock()
	c.voices = vs
	c.voicesAt = c.now()
	c.mu.Unlock()
	return append([]Voice(nil), vs...), nil
}

// cachedVoices returns a copy of the cached list (nil when there is none)
// and whether it is still within the TTL.
func (c *Client) cachedVoices() ([]Voice, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.voices == nil {
		return nil, false
	}
	age := c.now().Sub(c.voicesAt)
	return append([]Voice(nil), c.voices...), age >= 0 && age < c.voicesTTL
}

func (c *Client) fetchVoices(ctx context.Context) ([]Voice, error) {
	ctx, cancel := context.WithTimeout(ctx, c.connectTimeout+c.receiveTimeout)
	defer cancel()

	url := c.voicesURL + "&Sec-MS-GEC=" + c.gecToken() + "&Sec-MS-GEC-Version=" + secMSGECVersion
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("edgetts: voices: %w", scrubURL(err))
	}
	h := req.Header
	h.Set("Authority", "speech.platform.bing.com")
	h.Set("Sec-CH-UA", secCHUA)
	h.Set("Sec-CH-UA-Mobile", "?0")
	h.Set("Accept", "*/*")
	h.Set("Sec-Fetch-Site", "none")
	h.Set("Sec-Fetch-Mode", "cors")
	h.Set("Sec-Fetch-Dest", "empty")
	h.Set("User-Agent", userAgent)
	h.Set("Accept-Language", acceptLanguage)
	h.Set("Cookie", "muid="+randomHex(16, true)+";")
	// Accept-Encoding is left to net/http (gzip, decoded transparently): the
	// standard library cannot decode the br/zstd Edge advertises.

	resp, err := c.httpClient.Do(req)
	if err != nil {
		if ctxErr := ctx.Err(); ctxErr != nil {
			return nil, fmt.Errorf("edgetts: voices: %w", ctxErr)
		}
		return nil, fmt.Errorf("edgetts: voices: %w", scrubURL(err))
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		io.Copy(io.Discard, io.LimitReader(resp.Body, 64<<10))
		return nil, c.statusError("voices", resp)
	}

	body, err := io.ReadAll(io.LimitReader(resp.Body, maxVoicesBody+1))
	if err != nil {
		return nil, fmt.Errorf("edgetts: voices: read: %w", err)
	}
	if len(body) > maxVoicesBody {
		return nil, fmt.Errorf("%w: voice list larger than %d bytes", ErrProtocol, maxVoicesBody)
	}
	var raw []Voice
	if err := json.Unmarshal(body, &raw); err != nil {
		return nil, fmt.Errorf("%w: voice list is not JSON: %v", ErrProtocol, err)
	}
	vs := make([]Voice, 0, len(raw))
	for _, v := range raw {
		if v.ShortName == "" {
			continue
		}
		if v.FriendlyName == "" {
			v.FriendlyName = v.ShortName
		}
		vs = append(vs, v)
	}
	if len(vs) == 0 {
		return nil, fmt.Errorf("%w: empty voice list", ErrProtocol)
	}
	return vs, nil
}

// ReaderVoices applies the reader's filter to a full voice list, in the
// order the old server used: Vietnamese voices first (Locale "vi-..."), then
// the multilingual voices (ShortName contains "Multilingual").
func ReaderVoices(all []Voice) []Voice {
	out := make([]Voice, 0, 32)
	for _, v := range all {
		if strings.HasPrefix(v.Locale, "vi-") {
			out = append(out, v)
		}
	}
	for _, v := range all {
		if strings.Contains(v.ShortName, "Multilingual") {
			out = append(out, v)
		}
	}
	return out
}
