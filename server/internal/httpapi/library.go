package httpapi

import (
	"encoding/json"
	"errors"
	"net/http"

	"mythlab/internal/auth"
	"mythlab/internal/library"
	"mythlab/internal/userlib"
)

const (
	libraryPath       = "/api/library"
	maxLibraryBody    = 256 << 10
	maxLibraryEntries = 200
)

type libraryBody struct {
	Entries []userlib.Entry `json:"entries"`
	Now     int64           `json:"now"`
}

// apiLibrary: like /api/progress, for followed stories and bookmarks of the
// signed-in account. There is no global mode: a session is required.
func (s *Server) apiLibrary(w http.ResponseWriter, r *http.Request, q map[string]string, user *auth.User) {
	if s.o.Auth == nil || s.o.Users == nil {
		s.writeErr(w, r, http.StatusNotFound, "no_route", "không có API này")
		return
	}
	if user == nil {
		s.writeErr(w, r, http.StatusUnauthorized, "unauthorized", "cần đăng nhập Google")
		return
	}
	st := s.o.Users.Library(user.ID)
	switch r.Method {
	case http.MethodGet, http.MethodHead:
		since, err := intParam(q, "since", 0)
		if err != nil {
			s.fail(w, r, err)
			return
		}
		now := st.Now()
		s.writeJSON(w, r, http.StatusOK, libraryBody{st.Since(int64(since)), now}, "")
	case http.MethodPut:
		var in struct {
			Entries []userlib.Entry `json:"entries"`
		}
		dec := json.NewDecoder(http.MaxBytesReader(w, r.Body, maxLibraryBody))
		if err := dec.Decode(&in); err != nil {
			var mbe *http.MaxBytesError
			if errors.As(err, &mbe) {
				s.writeErr(w, r, http.StatusRequestEntityTooLarge, "too_large", "dữ liệu quá lớn")
			} else {
				s.fail(w, r, &library.Error{Status: http.StatusBadRequest, Code: "bad_body", Msg: "nội dung không hợp lệ"})
			}
			return
		}
		if len(in.Entries) > maxLibraryEntries {
			s.writeErr(w, r, http.StatusRequestEntityTooLarge, "too_many", "quá nhiều mục")
			return
		}
		out := st.Apply(in.Entries)
		s.writeJSON(w, r, http.StatusOK, libraryBody{out, st.Now()}, "")
	default:
		w.Header().Set("Allow", "GET, HEAD, PUT, OPTIONS")
		s.writeErr(w, r, http.StatusMethodNotAllowed, "method_not_allowed", "chỉ hỗ trợ GET/PUT")
	}
}
