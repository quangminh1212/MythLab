package httpapi

import (
	"encoding/json"
	"errors"
	"net/http"

	"mythlab/internal/library"
	"mythlab/internal/progress"
)

const (
	progressPath       = "/api/progress"
	maxProgressBody    = 256 << 10
	maxProgressEntries = 200
)

type progressBody struct {
	Entries []progress.Entry `json:"entries"`
	// Now is the server clock (ms): clients correct their clock skew with it
	// and use it as the next ?since= cursor.
	Now int64 `json:"now"`
}

// apiProgress: GET ?since=<ms> lists the entries changed since then; PUT
// {entries:[...]} merges entries and answers with their resulting state.
func (s *Server) apiProgress(w http.ResponseWriter, r *http.Request, q map[string]string) {
	st := s.o.Progress
	if st == nil {
		s.writeErr(w, r, http.StatusNotFound, "no_route", "không có API này")
		return
	}
	switch r.Method {
	case http.MethodGet, http.MethodHead:
		since, err := intParam(q, "since", 0)
		if err != nil {
			s.fail(w, r, err)
			return
		}
		now := st.Now()
		s.writeJSON(w, r, http.StatusOK, progressBody{st.Since(int64(since)), now}, "")
	case http.MethodPut:
		var in struct {
			Entries []progress.Entry `json:"entries"`
		}
		dec := json.NewDecoder(http.MaxBytesReader(w, r.Body, maxProgressBody))
		if err := dec.Decode(&in); err != nil {
			var mbe *http.MaxBytesError
			if errors.As(err, &mbe) {
				s.writeErr(w, r, http.StatusRequestEntityTooLarge, "too_large", "dữ liệu quá lớn")
			} else {
				s.fail(w, r, &library.Error{Status: http.StatusBadRequest, Code: "bad_body", Msg: "nội dung không hợp lệ"})
			}
			return
		}
		if len(in.Entries) > maxProgressEntries {
			s.writeErr(w, r, http.StatusRequestEntityTooLarge, "too_many", "quá nhiều mục")
			return
		}
		out := st.Apply(in.Entries)
		s.writeJSON(w, r, http.StatusOK, progressBody{out, st.Now()}, "")
	default:
		w.Header().Set("Allow", "GET, HEAD, PUT, OPTIONS")
		s.writeErr(w, r, http.StatusMethodNotAllowed, "method_not_allowed", "chỉ hỗ trợ GET/PUT")
	}
}
