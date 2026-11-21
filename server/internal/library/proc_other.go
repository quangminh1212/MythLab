//go:build !windows

package library

import "os/exec"

func hideWindow(*exec.Cmd) {}
