#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
: "${ANDROID_SDK_ROOT:?Set ANDROID_SDK_ROOT}"
: "${ECJ_JAR:?Set ECJ_JAR to Eclipse Java compiler jar}"
: "${CELLBLOCK_KEYSTORE:?Set CELLBLOCK_KEYSTORE to your private signing keystore}"
: "${CELLBLOCK_KEY_PASSWORD:?Set CELLBLOCK_KEY_PASSWORD}"
bt="$ANDROID_SDK_ROOT/build-tools/35.0.0"
platform="$ANDROID_SDK_ROOT/platforms/android-35/android.jar"
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT
mkdir -p "$build_dir/classes" "$build_dir/dex" ../../public/downloads
"$bt/aapt" package -f -M AndroidManifest.xml -S res -I "$platform" -F "$build_dir/base.apk"
java -jar "$ECJ_JAR" -1.8 -proc:none -bootclasspath "$platform" -d "$build_dir/classes" src/world/africandroid/cellblock/MainActivity.java
mapfile -t class_files < <(find "$build_dir/classes" -name '*.class')
"$bt/d8" --min-api 26 --lib "$platform" --output "$build_dir/dex" "${class_files[@]}"
cp "$build_dir/base.apk" "$build_dir/app.apk"
(cd "$build_dir/dex" && zip -q "$build_dir/app.apk" classes.dex)
"$bt/zipalign" -f 4 "$build_dir/app.apk" "$build_dir/aligned.apk"
"$bt/apksigner" sign --ks "$CELLBLOCK_KEYSTORE" --ks-key-alias cellblock --ks-pass env:CELLBLOCK_KEY_PASSWORD --key-pass env:CELLBLOCK_KEY_PASSWORD --out ../../public/downloads/CellblockCatAndMouse.apk "$build_dir/aligned.apk"
"$bt/apksigner" verify --verbose ../../public/downloads/CellblockCatAndMouse.apk
(cd ../../public/downloads && sha256sum CellblockCatAndMouse.apk > CellblockCatAndMouse.apk.sha256)
