module.exports.RTCSessionDescription = global.RTCSessionDescription ||
	global.mozRTCSessionDescription;
module.exports.RTCPeerConnection = global.RTCPeerConnection ||
	global.mozRTCPeerConnection || global.webkitRTCPeerConnection;
module.exports.RTCIceCandidate = global.RTCIceCandidate ||
	global.mozRTCIceCandidate;
