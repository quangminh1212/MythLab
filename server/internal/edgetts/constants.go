package edgetts

// Every value in this file mirrors the Microsoft Edge Read-Aloud client and is
// rotated by Microsoft from time to time. When the service starts answering
// 403 for every request, compare this file with constants.py of the current
// edge-tts release (https://github.com/rany2/edge-tts) and update it here;
// nothing else in the package hard-codes these values.
//
// Reference: edge-tts 7.3.1.
const (
	// trustedClientToken identifies the Edge Read-Aloud extension.
	trustedClientToken = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"

	// chromiumFullVersion and chromiumMajorVersion are the Edge build the
	// client claims to be.
	chromiumFullVersion  = "143.0.3650.75"
	chromiumMajorVersion = "143"

	// secMSGECVersion is sent next to the Sec-MS-GEC token; the leading "2"
	// selects the v2 token format implemented in drm.go.
	secMSGECVersion = "2-" + chromiumFullVersion

	// userAgent is the Edge user agent for chromiumMajorVersion.
	userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" +
		" (KHTML, like Gecko) Chrome/" + chromiumMajorVersion + ".0.0.0 Safari/537.36" +
		" Edg/" + chromiumMajorVersion + ".0.0.0"

	// secCHUA is the client-hint header sent with the voice list request.
	secCHUA = `" Not;A Brand";v="99", "Microsoft Edge";v="` + chromiumMajorVersion +
		`", "Chromium";v="` + chromiumMajorVersion + `"`

	// extensionOrigin is the Origin of the Read-Aloud extension.
	extensionOrigin = "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold"

	acceptEncoding = "gzip, deflate, br, zstd"
	acceptLanguage = "en-US,en;q=0.9"

	baseURL = "speech.platform.bing.com/consumer/speech/synthesize/readaloud"

	// defaultWSSURL and defaultVoicesURL already carry the client token; the
	// per-request parameters are appended to them.
	defaultWSSURL    = "wss://" + baseURL + "/edge/v1?TrustedClientToken=" + trustedClientToken
	defaultVoicesURL = "https://" + baseURL + "/voices/list?trustedclienttoken=" + trustedClientToken

	// outputFormat is the only format the reader uses (48 kbit/s CBR MP3).
	outputFormat = "audio-24khz-48kbitrate-mono-mp3"

	// maxSSMLTextBytes is the service limit for the escaped text of one
	// request; longer texts are split over several sessions.
	maxSSMLTextBytes = 4096
)
