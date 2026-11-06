/* Doxhund Vault — dependency-free Node tests using the built-in test runner.
 *
 * Run: node web/js/vault.test.js  (from the repo root)
 * Uses node:test + node:assert; requires Node 18+ (global subtle crypto).
 */
"use strict";

const { test } = require("node:test");
const assert = require("node:assert");
const {
  encrypt,
  decrypt,
  deriveKey,
  PBKDF2_ITERATIONS,
} = require("./vault.js");

test("encrypt -> decrypt round-trips to the original plaintext", async () => {
  const plaintext = "Jane Doe • 742 Evergreen Terrace • (555) 555-0142";
  const envelope = await encrypt(plaintext, "correct horse battery staple");
  const recovered = await decrypt(envelope, "correct horse battery staple");
  assert.strictEqual(recovered, plaintext);
});

test("wrong password throws on decrypt", async () => {
  const envelope = await encrypt("secret data", "right-password");
  await assert.rejects(decrypt(envelope, "wrong-password"));
});

test("tampered ciphertext throws on decrypt", async () => {
  const envelope = await encrypt("secret data", "right-password");
  const tampered = {
    ...envelope,
    ciphertext: Buffer.from(envelope.ciphertext, "base64")
      .map((b, i) => (i === 3 ? (b ^ 0x01) & 0xff : b)) // flip a byte
      .toString("base64"),
  };
  await assert.rejects(decrypt(tampered, "right-password"));
});

test("envelope carries correct KDF/alg metadata and base64 fields", async () => {
  const envelope = await encrypt("secret data", "right-password");
  assert.strictEqual(envelope.kdf, "PBKDF2-SHA256");
  assert.strictEqual(envelope.iterations, 600000);
  assert.strictEqual(PBKDF2_ITERATIONS, 600000);
  assert.strictEqual(envelope.alg, "AES-256-GCM");
  for (const field of ["salt", "iv", "ciphertext"]) {
    assert.ok(typeof envelope[field] === "string" && envelope[field].length > 0);
    // Must be valid base64 round-tripping to non-empty bytes.
    assert.ok(Buffer.from(envelope[field], "base64").length > 0);
  }
});

test("deriveKey produces a 256-bit AES-GCM key for a fixed salt", async () => {
  const salt = new Uint8Array(16).fill(7);
  const key = await deriveKey("fixed-password", salt);
  // The vault's own key is deliberately non-extractable (can't be exfiltrated).
  // Its AES-GCM algorithm.length reflects the actual key size in bits.
  assert.strictEqual(key.type, "secret");
  assert.strictEqual(key.algorithm.name, "AES-GCM");
  assert.strictEqual(key.algorithm.length, 256, "key should be 256-bit AES-GCM");
  assert.strictEqual(key.extractable, false, "vault keys are non-extractable");
  await assert.rejects(crypto.subtle.exportKey("raw", key));

  // Do the real export length check on an extractable key derived identically
  // (same PBKDF2 params, same salt) to confirm the full pipeline yields 256 bits.
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode("fixed-password"),
    "PBKDF2",
    false,
    ["deriveKey"]
  );
  const extractable = await crypto.subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: PBKDF2_ITERATIONS, hash: "SHA-256" },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );
  const raw = await crypto.subtle.exportKey("raw", extractable);
  assert.strictEqual(raw.byteLength, 32, "256-bit AES-GCM key = 32 bytes");
});
