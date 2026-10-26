"""Node.js execution test verifying static/js/crypto_engine.js compliance."""

import json
import subprocess
import pytest


def test_crypto_engine_js_vectors():
    node_script = """
    const CE = require('./static/js/crypto_engine.js');

    // 1. Empty string test vectors
    const empty = CE.hashText('');
    const expectedEmpty = {
        md5: 'd41d8cd98f00b204e9800998ecf8427e',
        sha1: 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
        sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        sha384: '38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b',
        sha512: 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'
    };

    for (const [alg, exp] of Object.entries(expectedEmpty)) {
        if (empty[alg] !== exp) {
            console.error(`Empty mismatch on ${alg}: got ${empty[alg]}, expected ${exp}`);
            process.exit(1);
        }
    }

    // 2. Standard phrase test vectors
    const phrase = 'The quick brown fox jumps over the lazy dog';
    const fox = CE.hashText(phrase);
    const expectedFox = {
        md5: '9e107d9d372bb6826bd81d3542a419d6',
        sha1: '2fd4e1c67a2d28fced849ee1bb76e7391b93eb12',
        sha256: 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592',
        sha384: 'ca737f1014a48f4c0b6dd43cb177b0afd9e5169367544c494011e3317dbf9a509cb1e5dc1e85a941bbee3d7f2afbc9b1',
        sha512: '07e547d9586f6a73f73fbac0435ed76951218fb7d0c8d788a309d785436bbb642e93a252a954f23912547d1e8a3b5ed6e1bfd7097821233fa0538f3db854fee6'
    };

    for (const [alg, exp] of Object.entries(expectedFox)) {
        if (fox[alg] !== exp) {
            console.error(`Fox mismatch on ${alg}: got ${fox[alg]}, expected ${exp}`);
            process.exit(2);
        }
    }

    // 3. Chunk boundaries test: feed in 3 byte slices
    const h = CE.createHasher('sha256');
    const bytes = CE.stringToUtf8Bytes(phrase);
    for (let i = 0; i < bytes.length; i += 3) {
        h.update(bytes.subarray(i, Math.min(i + 3, bytes.length)));
    }
    const chunkedDigest = h.digest('hex');
    if (chunkedDigest !== expectedFox.sha256) {
        console.error(`Chunk boundary mismatch: got ${chunkedDigest}, expected ${expectedFox.sha256}`);
        process.exit(3);
    }

    console.log('ALL_JS_CRYPTO_TESTS_PASSED');
    """

    res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
    assert res.returncode == 0, f"Node script error: {res.stderr}"
    assert "ALL_JS_CRYPTO_TESTS_PASSED" in res.stdout
