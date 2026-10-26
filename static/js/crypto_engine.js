/**
 * Client-Side Cryptographic Engine for Hash Analysis Toolkit.
 * 
 * Provides pure JavaScript streaming / progressive chunked hashing for:
 * - MD5 (RFC 1321)
 * - SHA-1 (FIPS PUB 180-1)
 * - SHA-256 (FIPS PUB 180-4)
 * - SHA-384 (FIPS PUB 180-4)
 * - SHA-512 (FIPS PUB 180-4)
 * 
 * Features:
 * - True chunked streaming over File / Blob objects (does not load full file into memory)
 * - Non-blocking asynchronous progress reporting
 * - Full Unicode (UTF-8) text encoding support
 * - Zero external CDN dependencies
 */

(function (root, factory) {
    if (typeof module === "object" && module.exports) {
        module.exports = factory();
    } else {
        root.CryptoEngine = factory();
    }
})(typeof self !== "undefined" ? self : this, function () {
    "use strict";

    // -------------------------------------------------------------------------
    // Utilities
    // -------------------------------------------------------------------------
    const textEncoder = typeof TextEncoder !== "undefined" ? new TextEncoder() : null;

    function stringToUtf8Bytes(str) {
        if (textEncoder) {
            return textEncoder.encode(str);
        }
        const utf8 = [];
        for (let i = 0; i < str.length; i++) {
            let charcode = str.charCodeAt(i);
            if (charcode < 0x80) utf8.push(charcode);
            else if (charcode < 0x800) {
                utf8.push(0xc0 | (charcode >> 6), 0x80 | (charcode & 0x3f));
            } else if (charcode < 0xd800 || charcode >= 0xe000) {
                utf8.push(0xe0 | (charcode >> 12), 0x80 | ((charcode >> 6) & 0x3f), 0x80 | (charcode & 0x3f));
            } else {
                // surrogate pair
                i++;
                charcode = 0x10000 + (((charcode & 0x3ff) << 10) | (str.charCodeAt(i) & 0x3ff));
                utf8.push(
                    0xf0 | (charcode >> 18),
                    0x80 | ((charcode >> 12) & 0x3f),
                    0x80 | ((charcode >> 6) & 0x3f),
                    0x80 | (charcode & 0x3f)
                );
            }
        }
        return new Uint8Array(utf8);
    }

    function bytesToHex(bytes) {
        let hex = "";
        for (let i = 0; i < bytes.length; i++) {
            const b = bytes[i];
            hex += (b < 16 ? "0" : "") + b.toString(16);
        }
        return hex;
    }

    // -------------------------------------------------------------------------
    // 1. Progressive MD5 Implementation (RFC 1321)
    // -------------------------------------------------------------------------
    class MD5Hasher {
        constructor() {
            this.reset();
        }

        reset() {
            this.state = new Int32Array([1732584193, -271733879, -1732584194, 271733878]);
            this.buffer = new Uint8Array(64);
            this.bufferLength = 0;
            this.bytesProcessed = 0;
        }

        update(data) {
            const bytes = data instanceof Uint8Array ? data : new Uint8Array(data.buffer || data);
            let offset = 0;
            const len = bytes.length;
            this.bytesProcessed += len;

            if (this.bufferLength > 0) {
                const needed = 64 - this.bufferLength;
                if (len >= needed) {
                    this.buffer.set(bytes.subarray(0, needed), this.bufferLength);
                    this._processBlock(this.buffer);
                    offset += needed;
                    this.bufferLength = 0;
                } else {
                    this.buffer.set(bytes, this.bufferLength);
                    this.bufferLength += len;
                    return this;
                }
            }

            while (offset + 64 <= len) {
                this._processBlock(bytes.subarray(offset, offset + 64));
                offset += 64;
            }

            if (offset < len) {
                this.buffer.set(bytes.subarray(offset), 0);
                this.bufferLength = len - offset;
            }
            return this;
        }

        digest(format = "hex") {
            const totalBits = this.bytesProcessed * 8;
            const padLen = this.bufferLength < 56 ? 56 - this.bufferLength : 120 - this.bufferLength;
            const padding = new Uint8Array(padLen + 8);
            padding[0] = 0x80;

            const lowBits = totalBits >>> 0;
            const highBits = Math.floor(this.bytesProcessed / 0x20000000) >>> 0;

            padding[padLen] = lowBits & 0xff;
            padding[padLen + 1] = (lowBits >>> 8) & 0xff;
            padding[padLen + 2] = (lowBits >>> 16) & 0xff;
            padding[padLen + 3] = (lowBits >>> 24) & 0xff;
            padding[padLen + 4] = highBits & 0xff;
            padding[padLen + 5] = (highBits >>> 8) & 0xff;
            padding[padLen + 6] = (highBits >>> 16) & 0xff;
            padding[padLen + 7] = (highBits >>> 24) & 0xff;

            this.update(padding);

            const out = new Uint8Array(16);
            for (let i = 0; i < 4; i++) {
                const w = this.state[i];
                out[i * 4] = w & 0xff;
                out[i * 4 + 1] = (w >>> 8) & 0xff;
                out[i * 4 + 2] = (w >>> 16) & 0xff;
                out[i * 4 + 3] = (w >>> 24) & 0xff;
            }
            return format === "hex" ? bytesToHex(out) : out;
        }

        _processBlock(chunk) {
            const X = new Int32Array(16);
            for (let i = 0; i < 16; i++) {
                X[i] = chunk[i * 4] | (chunk[i * 4 + 1] << 8) | (chunk[i * 4 + 2] << 16) | (chunk[i * 4 + 3] << 24);
            }

            let [a, b, c, d] = this.state;

            function rot(x, s) { return (x << s) | (x >>> (32 - s)); }
            function ff(a, b, c, d, x, s, t) { return (b + rot((a + ((b & c) | (~b & d)) + x + t) | 0, s)) | 0; }
            function gg(a, b, c, d, x, s, t) { return (b + rot((a + ((b & d) | (c & ~d)) + x + t) | 0, s)) | 0; }
            function hh(a, b, c, d, x, s, t) { return (b + rot((a + (b ^ c ^ d) + x + t) | 0, s)) | 0; }
            function ii(a, b, c, d, x, s, t) { return (b + rot((a + (c ^ (b | ~d)) + x + t) | 0, s)) | 0; }

            // Round 1
            a = ff(a, b, c, d, X[0], 7, -680876936); d = ff(d, a, b, c, X[1], 12, -389564586);
            c = ff(c, d, a, b, X[2], 17, 606105819); b = ff(b, c, d, a, X[3], 22, -1044525330);
            a = ff(a, b, c, d, X[4], 7, -176418897); d = ff(d, a, b, c, X[5], 12, 1200080426);
            c = ff(c, d, a, b, X[6], 17, -1473231341); b = ff(b, c, d, a, X[7], 22, -45705983);
            a = ff(a, b, c, d, X[8], 7, 1770035416); d = ff(d, a, b, c, X[9], 12, -1958414417);
            c = ff(c, d, a, b, X[10], 17, -42063); b = ff(b, c, d, a, X[11], 22, -1990404162);
            a = ff(a, b, c, d, X[12], 7, 1804603682); d = ff(d, a, b, c, X[13], 12, -40341101);
            c = ff(c, d, a, b, X[14], 17, -1502002290); b = ff(b, c, d, a, X[15], 22, 1236535329);

            // Round 2
            a = gg(a, b, c, d, X[1], 5, -165796510); d = gg(d, a, b, c, X[6], 9, -1069501632);
            c = gg(c, d, a, b, X[11], 14, 643717713); b = gg(b, c, d, a, X[0], 20, -373897302);
            a = gg(a, b, c, d, X[5], 5, -701558691); d = gg(d, a, b, c, X[10], 9, 38016083);
            c = gg(c, d, a, b, X[15], 14, -660478335); b = gg(b, c, d, a, X[4], 20, -405537848);
            a = gg(a, b, c, d, X[9], 5, 568446438); d = gg(d, a, b, c, X[14], 9, -1019803690);
            c = gg(c, d, a, b, X[3], 14, -187363961); b = gg(b, c, d, a, X[8], 20, 1163531501);
            a = gg(a, b, c, d, X[13], 5, -1444681467); d = gg(d, a, b, c, X[2], 9, -51403784);
            c = gg(c, d, a, b, X[7], 14, 1735328473); b = gg(b, c, d, a, X[12], 20, -1926607734);

            // Round 3
            a = hh(a, b, c, d, X[5], 4, -378558); d = hh(d, a, b, c, X[8], 11, -2022574463);
            c = hh(c, d, a, b, X[11], 16, 1839030562); b = hh(b, c, d, a, X[14], 23, -35309556);
            a = hh(a, b, c, d, X[1], 4, -1530992060); d = hh(d, a, b, c, X[4], 11, 1272893353);
            c = hh(c, d, a, b, X[7], 16, -155497632); b = hh(b, c, d, a, X[10], 23, -1094730640);
            a = hh(a, b, c, d, X[13], 4, 681279174); d = hh(d, a, b, c, X[0], 11, -358537222);
            c = hh(c, d, a, b, X[3], 16, -722521979); b = hh(b, c, d, a, X[6], 23, 76029189);
            a = hh(a, b, c, d, X[9], 4, -640364487); d = hh(d, a, b, c, X[12], 11, -421815835);
            c = hh(c, d, a, b, X[15], 16, 530742520); b = hh(b, c, d, a, X[2], 23, -995338651);

            // Round 4
            a = ii(a, b, c, d, X[0], 6, -198630844); d = ii(d, a, b, c, X[7], 10, 1126891415);
            c = ii(c, d, a, b, X[14], 15, -1416354905); b = ii(b, c, d, a, X[5], 21, -57434055);
            a = ii(a, b, c, d, X[12], 6, 1700485571); d = ii(d, a, b, c, X[3], 10, -1894986606);
            c = ii(c, d, a, b, X[10], 15, -1051523); b = ii(b, c, d, a, X[1], 21, -2054922799);
            a = ii(a, b, c, d, X[8], 6, 1873313359); d = ii(d, a, b, c, X[15], 10, -30611744);
            c = ii(c, d, a, b, X[6], 15, -1560198380); b = ii(b, c, d, a, X[13], 21, 1309151649);
            a = ii(a, b, c, d, X[4], 6, -145523070); d = ii(d, a, b, c, X[11], 10, -1120210379);
            c = ii(c, d, a, b, X[2], 15, 718787259); b = ii(b, c, d, a, X[9], 21, -343485551);

            this.state[0] = (this.state[0] + a) | 0;
            this.state[1] = (this.state[1] + b) | 0;
            this.state[2] = (this.state[2] + c) | 0;
            this.state[3] = (this.state[3] + d) | 0;
        }
    }

    // -------------------------------------------------------------------------
    // 2. Progressive SHA-1 Implementation (FIPS PUB 180-1)
    // -------------------------------------------------------------------------
    class SHA1Hasher {
        constructor() {
            this.reset();
        }

        reset() {
            this.state = new Int32Array([0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]);
            this.buffer = new Uint8Array(64);
            this.bufferLength = 0;
            this.bytesProcessed = 0;
        }

        update(data) {
            const bytes = data instanceof Uint8Array ? data : new Uint8Array(data.buffer || data);
            let offset = 0;
            const len = bytes.length;
            this.bytesProcessed += len;

            if (this.bufferLength > 0) {
                const needed = 64 - this.bufferLength;
                if (len >= needed) {
                    this.buffer.set(bytes.subarray(0, needed), this.bufferLength);
                    this._processBlock(this.buffer);
                    offset += needed;
                    this.bufferLength = 0;
                } else {
                    this.buffer.set(bytes, this.bufferLength);
                    this.bufferLength += len;
                    return this;
                }
            }

            while (offset + 64 <= len) {
                this._processBlock(bytes.subarray(offset, offset + 64));
                offset += 64;
            }

            if (offset < len) {
                this.buffer.set(bytes.subarray(offset), 0);
                this.bufferLength = len - offset;
            }
            return this;
        }

        digest(format = "hex") {
            const totalBits = this.bytesProcessed * 8;
            const padLen = this.bufferLength < 56 ? 56 - this.bufferLength : 120 - this.bufferLength;
            const padding = new Uint8Array(padLen + 8);
            padding[0] = 0x80;

            const lowBits = totalBits >>> 0;
            const highBits = Math.floor(this.bytesProcessed / 0x20000000) >>> 0;

            padding[padLen] = (highBits >>> 24) & 0xff;
            padding[padLen + 1] = (highBits >>> 16) & 0xff;
            padding[padLen + 2] = (highBits >>> 8) & 0xff;
            padding[padLen + 3] = highBits & 0xff;
            padding[padLen + 4] = (lowBits >>> 24) & 0xff;
            padding[padLen + 5] = (lowBits >>> 16) & 0xff;
            padding[padLen + 6] = (lowBits >>> 8) & 0xff;
            padding[padLen + 7] = lowBits & 0xff;

            this.update(padding);

            const out = new Uint8Array(20);
            for (let i = 0; i < 5; i++) {
                const w = this.state[i];
                out[i * 4] = (w >>> 24) & 0xff;
                out[i * 4 + 1] = (w >>> 16) & 0xff;
                out[i * 4 + 2] = (w >>> 8) & 0xff;
                out[i * 4 + 3] = w & 0xff;
            }
            return format === "hex" ? bytesToHex(out) : out;
        }

        _processBlock(chunk) {
            const W = new Int32Array(80);
            for (let i = 0; i < 16; i++) {
                W[i] = (chunk[i * 4] << 24) | (chunk[i * 4 + 1] << 16) | (chunk[i * 4 + 2] << 8) | chunk[i * 4 + 3];
            }
            for (let i = 16; i < 80; i++) {
                const x = W[i - 3] ^ W[i - 8] ^ W[i - 14] ^ W[i - 16];
                W[i] = (x << 1) | (x >>> 31);
            }

            let [a, b, c, d, e] = this.state;

            for (let i = 0; i < 80; i++) {
                let f, k;
                if (i < 20) {
                    f = (b & c) | (~b & d);
                    k = 0x5a827999;
                } else if (i < 40) {
                    f = b ^ c ^ d;
                    k = 0x6ed9eba1;
                } else if (i < 60) {
                    f = (b & c) | (b & d) | (c & d);
                    k = 0x8f1bbcdc;
                } else {
                    f = b ^ c ^ d;
                    k = 0xca62c1d6;
                }
                const temp = (((a << 5) | (a >>> 27)) + f + e + k + W[i]) | 0;
                e = d;
                d = c;
                c = (b << 30) | (b >>> 2);
                b = a;
                a = temp;
            }

            this.state[0] = (this.state[0] + a) | 0;
            this.state[1] = (this.state[1] + b) | 0;
            this.state[2] = (this.state[2] + c) | 0;
            this.state[3] = (this.state[3] + d) | 0;
            this.state[4] = (this.state[4] + e) | 0;
        }
    }

    // -------------------------------------------------------------------------
    // 3. Progressive SHA-256 Implementation (FIPS PUB 180-4)
    // -------------------------------------------------------------------------
    const K256 = new Int32Array([
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]);

    class SHA256Hasher {
        constructor() {
            this.reset();
        }

        reset() {
            this.state = new Int32Array([
                0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
            ]);
            this.buffer = new Uint8Array(64);
            this.bufferLength = 0;
            this.bytesProcessed = 0;
        }

        update(data) {
            const bytes = data instanceof Uint8Array ? data : new Uint8Array(data.buffer || data);
            let offset = 0;
            const len = bytes.length;
            this.bytesProcessed += len;

            if (this.bufferLength > 0) {
                const needed = 64 - this.bufferLength;
                if (len >= needed) {
                    this.buffer.set(bytes.subarray(0, needed), this.bufferLength);
                    this._processBlock(this.buffer);
                    offset += needed;
                    this.bufferLength = 0;
                } else {
                    this.buffer.set(bytes, this.bufferLength);
                    this.bufferLength += len;
                    return this;
                }
            }

            while (offset + 64 <= len) {
                this._processBlock(bytes.subarray(offset, offset + 64));
                offset += 64;
            }

            if (offset < len) {
                this.buffer.set(bytes.subarray(offset), 0);
                this.bufferLength = len - offset;
            }
            return this;
        }

        digest(format = "hex") {
            const totalBits = this.bytesProcessed * 8;
            const padLen = this.bufferLength < 56 ? 56 - this.bufferLength : 120 - this.bufferLength;
            const padding = new Uint8Array(padLen + 8);
            padding[0] = 0x80;

            const lowBits = totalBits >>> 0;
            const highBits = Math.floor(this.bytesProcessed / 0x20000000) >>> 0;

            padding[padLen] = (highBits >>> 24) & 0xff;
            padding[padLen + 1] = (highBits >>> 16) & 0xff;
            padding[padLen + 2] = (highBits >>> 8) & 0xff;
            padding[padLen + 3] = highBits & 0xff;
            padding[padLen + 4] = (lowBits >>> 24) & 0xff;
            padding[padLen + 5] = (lowBits >>> 16) & 0xff;
            padding[padLen + 6] = (lowBits >>> 8) & 0xff;
            padding[padLen + 7] = lowBits & 0xff;

            this.update(padding);

            const out = new Uint8Array(32);
            for (let i = 0; i < 8; i++) {
                const w = this.state[i];
                out[i * 4] = (w >>> 24) & 0xff;
                out[i * 4 + 1] = (w >>> 16) & 0xff;
                out[i * 4 + 2] = (w >>> 8) & 0xff;
                out[i * 4 + 3] = w & 0xff;
            }
            return format === "hex" ? bytesToHex(out) : out;
        }

        _processBlock(chunk) {
            const W = new Int32Array(64);
            for (let i = 0; i < 16; i++) {
                W[i] = (chunk[i * 4] << 24) | (chunk[i * 4 + 1] << 16) | (chunk[i * 4 + 2] << 8) | chunk[i * 4 + 3];
            }
            for (let i = 16; i < 64; i++) {
                const s0 = ((W[i - 15] >>> 7) | (W[i - 15] << 25)) ^ ((W[i - 15] >>> 18) | (W[i - 15] << 14)) ^ (W[i - 15] >>> 3);
                const s1 = ((W[i - 2] >>> 17) | (W[i - 2] << 15)) ^ ((W[i - 2] >>> 19) | (W[i - 2] << 13)) ^ (W[i - 2] >>> 10);
                W[i] = (W[i - 16] + s0 + W[i - 7] + s1) | 0;
            }

            let [a, b, c, d, e, f, g, h] = this.state;

            for (let i = 0; i < 64; i++) {
                const S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
                const ch = (e & f) ^ (~e & g);
                const temp1 = (h + S1 + ch + K256[i] + W[i]) | 0;
                const S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
                const maj = (a & b) ^ (a & c) ^ (b & c);
                const temp2 = (S0 + maj) | 0;

                h = g;
                g = f;
                f = e;
                e = (d + temp1) | 0;
                d = c;
                c = b;
                b = a;
                a = (temp1 + temp2) | 0;
            }

            this.state[0] = (this.state[0] + a) | 0;
            this.state[1] = (this.state[1] + b) | 0;
            this.state[2] = (this.state[2] + c) | 0;
            this.state[3] = (this.state[3] + d) | 0;
            this.state[4] = (this.state[4] + e) | 0;
            this.state[5] = (this.state[5] + f) | 0;
            this.state[6] = (this.state[6] + g) | 0;
            this.state[7] = (this.state[7] + h) | 0;
        }
    }

    // -------------------------------------------------------------------------
    // 4 & 5. Progressive SHA-512 & SHA-384 Implementations (BigInt 64-bit)
    // -------------------------------------------------------------------------
    const K512 = [
        0x428a2f98d728ae22n, 0x7137449123ef65cdn, 0xb5c0fbcfec4d3b2fn, 0xe9b5dba58189dbbcn,
        0x3956c25bf348b538n, 0x59f111f1b605d019n, 0x923f82a4af194f9bn, 0xab1c5ed5da6d8118n,
        0xd807aa98a3030242n, 0x12835b0145706fben, 0x243185be4ee4b28cn, 0x550c7dc3d5ffb4e2n,
        0x72be5d74f27b896fn, 0x80deb1fe3b1696b1n, 0x9bdc06a725c71235n, 0xc19bf174cf692694n,
        0xe49b69c19ef14ad2n, 0xefbe4786384f25e3n, 0x0fc19dc68b8cd5b5n, 0x240ca1cc77ac9c65n,
        0x2de92c6f592b0275n, 0x4a7484aa6ea6e483n, 0x5cb0a9dcbd41fbd4n, 0x76f988da831153b5n,
        0x983e5152ee66dfabn, 0xa831c66d2db43210n, 0xb00327c898fb213fn, 0xbf597fc7beef0ee4n,
        0xc6e00bf33da88fc2n, 0xd5a79147930aa725n, 0x06ca6351e003826fn, 0x142929670a0e6e70n,
        0x27b70a8546d22ffcn, 0x2e1b21385c26c926n, 0x4d2c6dfc5ac42aedn, 0x53380d139d95b3dfn,
        0x650a73548baf63den, 0x766a0abb3c77b2a8n, 0x81c2c92e47edaee6n, 0x92722c851482353bn,
        0xa2bfe8a14cf10364n, 0xa81a664bbc423001n, 0xc24b8b70d0f89791n, 0xc76c51a30654be30n,
        0xd192e819d6ef5218n, 0xd69906245565a910n, 0xf40e35855771202an, 0x106aa07032bbd1b8n,
        0x19a4c116b8d2d0c8n, 0x1e376c085141ab53n, 0x2748774cdf8eeb99n, 0x34b0bcb5e19b48a8n,
        0x391c0cb3c5c95a63n, 0x4ed8aa4ae3418acbn, 0x5b9cca4f7763e373n, 0x682e6ff3d6b2b8a3n,
        0x748f82ee5defb2fcn, 0x78a5636f43172f60n, 0x84c87814a1f0ab72n, 0x8cc702081a6439ecn,
        0x90befffa23631e28n, 0xa4506cebde82bde9n, 0xbef9a3f7b2c67915n, 0xc67178f2e372532bn,
        0xca273eceea26619cn, 0xd186b8c721c0c207n, 0xeada7dd6cde0eb1en, 0xf57d4f7fee6ed178n,
        0x06f067aa72176fban, 0x0a637dc5a2c898a6n, 0x113f9804bef90daen, 0x1b710b35131c471bn,
        0x28db77f523047d84n, 0x32caab7b40c72493n, 0x3c9ebe0a15c9bebcn, 0x431d67c49c100d4cn,
        0x4cc5d4becb3e42b6n, 0x597f299cfc657e2an, 0x5fcb6fab3ad6faecn, 0x6c44198c4a475817n
    ];

    const MASK64 = 0xffffffffffffffffn;

    function rotr64(x, n) {
        const nb = BigInt(n);
        return ((x >> nb) | (x << (64n - nb))) & MASK64;
    }

    class SHA512Hasher {
        constructor() {
            this.reset();
        }

        reset() {
            this.state = [
                0x6a09e667f3bcc908n, 0xbb67ae8584caa73bn, 0x3c6ef372fe94f82bn, 0xa54ff53a5f1d36f1n,
                0x510e527fade682d1n, 0x9b05688c2b3e6c1fn, 0x1f83d9abfb41bd6bn, 0x5be0cd19137e2179n
            ];
            this.buffer = new Uint8Array(128);
            this.bufferLength = 0;
            this.bytesProcessed = 0;
        }

        update(data) {
            const bytes = data instanceof Uint8Array ? data : new Uint8Array(data.buffer || data);
            let offset = 0;
            const len = bytes.length;
            this.bytesProcessed += len;

            if (this.bufferLength > 0) {
                const needed = 128 - this.bufferLength;
                if (len >= needed) {
                    this.buffer.set(bytes.subarray(0, needed), this.bufferLength);
                    this._processBlock(this.buffer);
                    offset += needed;
                    this.bufferLength = 0;
                } else {
                    this.buffer.set(bytes, this.bufferLength);
                    this.bufferLength += len;
                    return this;
                }
            }

            while (offset + 128 <= len) {
                this._processBlock(bytes.subarray(offset, offset + 128));
                offset += 128;
            }

            if (offset < len) {
                this.buffer.set(bytes.subarray(offset), 0);
                this.bufferLength = len - offset;
            }
            return this;
        }

        digest(format = "hex") {
            const totalBits = BigInt(this.bytesProcessed) * 8n;
            const padLen = this.bufferLength < 112 ? 112 - this.bufferLength : 240 - this.bufferLength;
            const padding = new Uint8Array(padLen + 16);
            padding[0] = 0x80;

            for (let i = 0; i < 16; i++) {
                padding[padLen + 15 - i] = Number((totalBits >> BigInt(i * 8)) & 0xffn);
            }

            this.update(padding);

            const out = new Uint8Array(64);
            for (let i = 0; i < 8; i++) {
                const w = this.state[i];
                for (let j = 0; j < 8; j++) {
                    out[i * 8 + j] = Number((w >> BigInt((7 - j) * 8)) & 0xffn);
                }
            }
            return format === "hex" ? bytesToHex(out) : out;
        }

        _processBlock(chunk) {
            const W = new Array(80);
            for (let i = 0; i < 16; i++) {
                let v = 0n;
                for (let j = 0; j < 8; j++) {
                    v = (v << 8n) | BigInt(chunk[i * 8 + j]);
                }
                W[i] = v;
            }

            for (let i = 16; i < 80; i++) {
                const s0 = rotr64(W[i - 15], 1) ^ rotr64(W[i - 15], 8) ^ (W[i - 15] >> 7n);
                const s1 = rotr64(W[i - 2], 19) ^ rotr64(W[i - 2], 61) ^ (W[i - 2] >> 6n);
                W[i] = (W[i - 16] + s0 + W[i - 7] + s1) & MASK64;
            }

            let [a, b, c, d, e, f, g, h] = this.state;

            for (let i = 0; i < 80; i++) {
                const S1 = rotr64(e, 14) ^ rotr64(e, 18) ^ rotr64(e, 41);
                const ch = (e & f) ^ (~e & g);
                const temp1 = (h + S1 + ch + K512[i] + W[i]) & MASK64;
                const S0 = rotr64(a, 28) ^ rotr64(a, 34) ^ rotr64(a, 39);
                const maj = (a & b) ^ (a & c) ^ (b & c);
                const temp2 = (S0 + maj) & MASK64;

                h = g;
                g = f;
                f = e;
                e = (d + temp1) & MASK64;
                d = c;
                c = b;
                b = a;
                a = (temp1 + temp2) & MASK64;
            }

            this.state[0] = (this.state[0] + a) & MASK64;
            this.state[1] = (this.state[1] + b) & MASK64;
            this.state[2] = (this.state[2] + c) & MASK64;
            this.state[3] = (this.state[3] + d) & MASK64;
            this.state[4] = (this.state[4] + e) & MASK64;
            this.state[5] = (this.state[5] + f) & MASK64;
            this.state[6] = (this.state[6] + g) & MASK64;
            this.state[7] = (this.state[7] + h) & MASK64;
        }
    }

    class SHA384Hasher extends SHA512Hasher {
        reset() {
            super.reset();
            this.state = [
                0xcbbb9d5dc1059ed8n, 0x629a292a367cd507n, 0x9159015a3070dd17n, 0x152fecd8f70e5939n,
                0x67332667ffc00b31n, 0x8eb44a8768581511n, 0xdb0c2e0d64f98fa7n, 0x47b5481dbefa4fa4n
            ];
        }

        digest(format = "hex") {
            const raw512 = super.digest("bytes");
            const out = raw512.subarray(0, 48); // Truncate to first 48 bytes (384 bits)
            return format === "hex" ? bytesToHex(out) : out;
        }
    }

    // -------------------------------------------------------------------------
    // Factory and High-Level Helper Functions
    // -------------------------------------------------------------------------
    function createHasher(algorithm) {
        const alg = (algorithm || "").toLowerCase().replace(/[^a-z0-9]/g, "");
        switch (alg) {
            case "md5": return new MD5Hasher();
            case "sha1": return new SHA1Hasher();
            case "sha256": return new SHA256Hasher();
            case "sha384": return new SHA384Hasher();
            case "sha512": return new SHA512Hasher();
            default:
                throw new Error(`Unsupported cryptographic algorithm: ${algorithm}`);
        }
    }

    /**
     * Synchronously hash text across multiple algorithms.
     */
    function hashText(text, algorithms = ["md5", "sha1", "sha256", "sha384", "sha512"]) {
        const bytes = stringToUtf8Bytes(text != null ? String(text) : "");
        const results = {};
        for (const alg of algorithms) {
            const hasher = createHasher(alg);
            hasher.update(bytes);
            results[alg] = hasher.digest("hex");
        }
        return results;
    }

    /**
     * Incrementally hash a browser File or Blob in streaming chunks without memory explosion.
     * Yields to the UI loop between chunks to enable responsive progress updates.
     * 
     * @param {File|Blob} file 
     * @param {string[]} algorithms 
     * @param {function} onProgress callback ({ percent, bytesProcessed, totalBytes })
     * @param {number} chunkSize default 2MB (2,097,152 bytes)
     * @returns {Promise<Object>} { totalBytes, hashes: { md5, sha1, ... } }
     */
    async function hashFileStreaming(file, algorithms = ["sha256"], onProgress = null, chunkSize = 2 * 1024 * 1024) {
        if (!file || typeof file.size !== "number") {
            throw new Error("Invalid file object provided for hashing.");
        }

        const totalBytes = file.size;
        const hashers = {};
        for (const alg of algorithms) {
            hashers[alg] = createHasher(alg);
        }

        // Special case: empty file (0 bytes)
        if (totalBytes === 0) {
            const emptyBytes = new Uint8Array(0);
            const results = {};
            for (const [alg, h] of Object.entries(hashers)) {
                h.update(emptyBytes);
                results[alg] = h.digest("hex");
            }
            if (onProgress) onProgress({ percent: 100, bytesProcessed: 0, totalBytes: 0 });
            return { totalBytes: 0, hashes: results };
        }

        let offset = 0;

        while (offset < totalBytes) {
            const end = Math.min(offset + chunkSize, totalBytes);
            const slice = file.slice(offset, end);
            const buffer = await slice.arrayBuffer();
            const chunkBytes = new Uint8Array(buffer);

            for (const h of Object.values(hashers)) {
                h.update(chunkBytes);
            }

            offset = end;
            const percent = Math.min(100, Math.round((offset / totalBytes) * 100));

            if (onProgress) {
                onProgress({ percent, bytesProcessed: offset, totalBytes });
            }

            // Yield to browser event loop
            await new Promise((resolve) => setTimeout(resolve, 0));
        }

        const hashes = {};
        for (const [alg, h] of Object.entries(hashers)) {
            hashes[alg] = h.digest("hex");
        }

        return { totalBytes, hashes };
    }

    return {
        MD5Hasher,
        SHA1Hasher,
        SHA256Hasher,
        SHA384Hasher,
        SHA512Hasher,
        createHasher,
        hashText,
        hashFileStreaming,
        stringToUtf8Bytes,
        bytesToHex,
    };
});
