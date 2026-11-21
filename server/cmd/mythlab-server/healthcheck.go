package main

import (
	"context"
	"fmt"
	"io"
	"net"
	"net/http"
	"strconv"
	"time"
)

// probeHost is the address a health probe dials for a server bound to host:
// a wildcard bind is reached through loopback.
func probeHost(host string) string {
	if host == "" || host == "0.0.0.0" || host == "::" || host == "[::]" {
		return "127.0.0.1"
	}
	return host
}

// healthcheck asks the server on host:port for /api/ping. It runs from the
// same machine, so the loopback exemption normally makes the key unnecessary;
// 401 (server.trust_loopback=false) still proves the server is up and answering.
func healthcheck(host string, port int, timeout time.Duration) error {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	u := "http://" + net.JoinHostPort(probeHost(host), strconv.Itoa(port)) + "/api/ping"
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u, nil)
	if err != nil {
		return err
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	io.Copy(io.Discard, io.LimitReader(resp.Body, 1<<16))
	if resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusUnauthorized {
		return nil
	}
	return fmt.Errorf("%s: HTTP %d", u, resp.StatusCode)
}
