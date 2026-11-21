//go:build windows

package main

import (
	"syscall"
	"unsafe"

	"golang.org/x/sys/windows"
)

var (
	user32  = windows.NewLazySystemDLL("user32.dll")
	shell32 = windows.NewLazySystemDLL("shell32.dll")

	procMessageBoxW         = user32.NewProc("MessageBoxW")
	procEnumWindows         = user32.NewProc("EnumWindows")
	procEnumThreadWindows   = user32.NewProc("EnumThreadWindows")
	procGetClassNameW       = user32.NewProc("GetClassNameW")
	procGetPropW            = user32.NewProc("GetPropW")
	procSetPropW            = user32.NewProc("SetPropW")
	procRemovePropW         = user32.NewProc("RemovePropW")
	procIsIconic            = user32.NewProc("IsIconic")
	procShowWindow          = user32.NewProc("ShowWindow")
	procSetForegroundWindow = user32.NewProc("SetForegroundWindow")
	procFlashWindow         = user32.NewProc("FlashWindow")
	procPostMessageW        = user32.NewProc("PostMessageW")
	procSetWindowLongPtrW   = user32.NewProc("SetWindowLongPtrW")
	procCallWindowProcW     = user32.NewProc("CallWindowProcW")
	procGetWindowPlacement  = user32.NewProc("GetWindowPlacement")
	procSetWindowPos        = user32.NewProc("SetWindowPos")
	procGetSystemMetrics    = user32.NewProc("GetSystemMetrics")
	procGetDpiForWindow     = user32.NewProc("GetDpiForWindow")
	procGetDpiForSystem     = user32.NewProc("GetDpiForSystem")
	procShellExecuteW       = shell32.NewProc("ShellExecuteW")
)

const (
	wmClose         = 0x0010
	wmEndSession    = 0x0016
	wmGetMinMaxInfo = 0x0024
	wmDpiChanged    = 0x02E0

	swHide     = 0
	swMaximize = 3
	swRestore  = 9

	swShowMinimized = 2
	swShowMaximized = 3

	wpfRestoreToMaximized = 0x0002

	swpNoMove     = 0x0002
	swpNoZOrder   = 0x0004
	swpNoActivate = 0x0010

	smCxScreen = 0
	smCyScreen = 1

	mbOK          = 0x00000000
	mbOKCancel    = 0x00000001
	mbYesNo       = 0x00000004
	mbIconError   = 0x00000010
	mbIconWarning = 0x00000030
	mbIconInfo    = 0x00000040
	mbSetFore     = 0x00010000
	mbTopMost     = 0x00040000

	idOK  = 1
	idYes = 6
)

// gwlpWndProc is GWLP_WNDPROC (-4) as the unsigned value the call takes.
var gwlpWndProc = ^uintptr(3)

type point struct{ X, Y int32 }

type rect struct{ Left, Top, Right, Bottom int32 }

type windowPlacement struct {
	Length           uint32
	Flags            uint32
	ShowCmd          uint32
	PtMinPosition    point
	PtMaxPosition    point
	RcNormalPosition rect
}

type minMaxInfo struct {
	PtReserved     point
	PtMaxSize      point
	PtMaxPosition  point
	PtMinTrackSize point
	PtMaxTrackSize point
}

// ptr turns an lParam that carries a pointer into that pointer. The detour
// through the variable's address keeps go vet's unsafe.Pointer check quiet;
// the memory belongs to the system for the duration of the message.
func ptr(lp uintptr) unsafe.Pointer { return *(*unsafe.Pointer)(unsafe.Pointer(&lp)) }

func utf16(s string) *uint16 {
	p, err := windows.UTF16PtrFromString(s)
	if err != nil { // an embedded NUL: cut there
		for i := 0; i < len(s); i++ {
			if s[i] == 0 {
				p, _ = windows.UTF16PtrFromString(s[:i])
				break
			}
		}
	}
	return p
}

// messageBox shows a modal box and returns the button id.
func messageBox(owner uintptr, text string, flags uintptr) int {
	r, _, _ := procMessageBoxW.Call(owner, uintptr(unsafe.Pointer(utf16(text))), uintptr(unsafe.Pointer(utf16(appTitle))), flags|mbSetFore)
	return int(r)
}

// findWindowWithProp returns the top-level window that carries the property.
func findWindowWithProp(name string) uintptr {
	p := utf16(name)
	var found uintptr
	cb := syscall.NewCallback(func(hwnd, _ uintptr) uintptr {
		if h, _, _ := procGetPropW.Call(hwnd, uintptr(unsafe.Pointer(p))); h != 0 {
			found = hwnd
			return 0 // stop
		}
		return 1
	})
	procEnumWindows.Call(cb, 0)
	return found
}

// threadWindows lists the top-level windows of this thread with the class.
func threadWindows(class string) []uintptr {
	var out []uintptr
	cb := syscall.NewCallback(func(hwnd, _ uintptr) uintptr {
		buf := make([]uint16, 64)
		n, _, _ := procGetClassNameW.Call(hwnd, uintptr(unsafe.Pointer(&buf[0])), uintptr(len(buf)))
		if windows.UTF16ToString(buf[:n]) == class {
			out = append(out, hwnd)
		}
		return 1
	})
	procEnumThreadWindows.Call(uintptr(windows.GetCurrentThreadId()), cb, 0)
	return out
}

func setProp(hwnd uintptr, name string) {
	procSetPropW.Call(hwnd, uintptr(unsafe.Pointer(utf16(name))), 1)
}

func removeProp(hwnd uintptr, name string) {
	procRemovePropW.Call(hwnd, uintptr(unsafe.Pointer(utf16(name))))
}

// activateWindow restores hwnd if it is minimised and brings it to the front.
func activateWindow(hwnd uintptr) bool {
	if r, _, _ := procIsIconic.Call(hwnd); r != 0 {
		procShowWindow.Call(hwnd, swRestore)
	}
	r, _, _ := procSetForegroundWindow.Call(hwnd)
	if r == 0 {
		procFlashWindow.Call(hwnd, 1) // Windows refused the focus change: blink the taskbar button
	}
	return r != 0
}

func postClose(hwnd uintptr) { procPostMessageW.Call(hwnd, wmClose, 0, 0) }

func showMaximized(hwnd uintptr) { procShowWindow.Call(hwnd, swMaximize) }

func hideWindow(hwnd uintptr) { procShowWindow.Call(hwnd, swHide) }

func resizeWindow(hwnd uintptr, w, h int) {
	procSetWindowPos.Call(hwnd, 0, 0, 0, uintptr(w), uintptr(h), swpNoMove|swpNoZOrder|swpNoActivate)
}

func moveWindow(hwnd uintptr, r rect) {
	procSetWindowPos.Call(hwnd, 0, uintptr(r.Left), uintptr(r.Top), uintptr(r.Right-r.Left), uintptr(r.Bottom-r.Top),
		swpNoZOrder|swpNoActivate)
}

// placement returns the restored (not maximised, not minimised) outer size of
// hwnd in pixels and whether the window is, or will be restored to, maximised.
func placement(hwnd uintptr) (w, h int, maximized, ok bool) {
	var wp windowPlacement
	wp.Length = uint32(unsafe.Sizeof(wp))
	if r, _, _ := procGetWindowPlacement.Call(hwnd, uintptr(unsafe.Pointer(&wp))); r == 0 {
		return 0, 0, false, false
	}
	maximized = wp.ShowCmd == swShowMaximized || (wp.ShowCmd == swShowMinimized && wp.Flags&wpfRestoreToMaximized != 0)
	return int(wp.RcNormalPosition.Right - wp.RcNormalPosition.Left), int(wp.RcNormalPosition.Bottom - wp.RcNormalPosition.Top), maximized, true
}

func primaryScreen() (w, h int) {
	cx, _, _ := procGetSystemMetrics.Call(smCxScreen)
	cy, _, _ := procGetSystemMetrics.Call(smCyScreen)
	return int(int32(cx)), int(int32(cy))
}

func systemDPI() int {
	if procGetDpiForSystem.Find() != nil {
		return 96
	}
	if d, _, _ := procGetDpiForSystem.Call(); d != 0 {
		return int(d)
	}
	return 96
}

func windowDPI(hwnd uintptr) int {
	if procGetDpiForWindow.Find() != nil {
		return systemDPI()
	}
	if d, _, _ := procGetDpiForWindow.Call(hwnd); d != 0 {
		return int(d)
	}
	return systemDPI()
}

// subclass replaces the window procedure of hwnd and returns the previous one.
func subclass(hwnd uintptr, proc func(hwnd, msg, wp, lp uintptr) uintptr) uintptr {
	prev, _, _ := procSetWindowLongPtrW.Call(hwnd, gwlpWndProc, syscall.NewCallback(proc))
	return prev
}

func callWindowProc(prev, hwnd, msg, wp, lp uintptr) uintptr {
	r, _, _ := procCallWindowProcW.Call(prev, hwnd, msg, wp, lp)
	return r
}

// shellOpen opens a URL or file with its default program.
func shellOpen(target string) bool {
	r, _, _ := procShellExecuteW.Call(0, uintptr(unsafe.Pointer(utf16("open"))), uintptr(unsafe.Pointer(utf16(target))), 0, 0, 1)
	return r > 32
}
