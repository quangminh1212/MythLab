package main

import (
	"net"
	"net/http"
	"net/http/httptest"
	"strconv"
	"testing"
	"time"
)

func TestHealthcheck(t *testing.T) {
	status := http.StatusOK
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/ping" {
			t.Errorf("path %q", r.URL.Path)
		}
		w.WriteHeader(status)
	}))
	defer srv.Close()
	_, ps, _ := net.SplitHostPort(srv.Listener.Addr().String())
	port, _ := strconv.Atoi(ps)

	for _, host := range []string{"127.0.0.1", "0.0.0.0", ""} {
		if err := healthcheck(host, port, time.Second); err != nil {
			t.Errorf("host %q: %v", host, err)
		}
	}
	status = http.StatusUnauthorized
	if err := healthcheck("127.0.0.1", port, time.Second); err != nil {
		t.Errorf("401 means alive: %v", err)
	}
	status = http.StatusInternalServerError
	if err := healthcheck("127.0.0.1", port, time.Second); err == nil {
		t.Error("500 must fail")
	}
	srv.Close()
	if err := healthcheck("127.0.0.1", port, time.Second); err == nil {
		t.Error("closed port must fail")
	}
}

func TestRunHealthcheckFlag(t *testing.T) {
	if run([]string{"--healthcheck", "--port", "1"}) != 1 {
		t.Fatal("unreachable server must exit 1")
	}
}
