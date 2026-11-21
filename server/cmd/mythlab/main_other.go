//go:build !windows

// Command mythlab is the MythLab desktop app. It exists for Windows only; on
// other systems run mythlab-server and open it in a browser.
package main

import (
	"fmt"
	"os"
)

func main() {
	fmt.Fprintln(os.Stderr, "mythlab: bản desktop chỉ có cho Windows; hãy chạy mythlab-server và mở bằng trình duyệt")
	os.Exit(1)
}
