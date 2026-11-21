//go:build windows

package library

import (
	"os/exec"
	"syscall"
)

// hideWindow keeps `gh auth token` from flashing a console window.
func hideWindow(cmd *exec.Cmd) {
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true, CreationFlags: 0x08000000}
}
