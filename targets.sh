#!/usr/bin/env bash
set -u
mkdir -p out/videos/targets
ok=0; fail=0
for spec in \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/33750f39-32ce-413c-a3e4-4ebd80f9ac46_1930882_invisible.mp4|out/videos/targets/00_B07-C10.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/370fd7bb-fde6-4bed-94a1-2ff0c7c86fa4_1930883_invisible.mp4|out/videos/targets/01_B07-C03.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/0c145b1b-0ada-4eb0-bf87-60f620eec323_1930889_invisible.mp4|out/videos/targets/02_B08-C09.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/ae97088b-98d4-405d-a63a-12cf981df6bd_1930891_invisible.mp4|out/videos/targets/03_B02-C10.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/64e3e668-c19a-430d-b6e4-26752393a937_1930923_invisible.mp4|out/videos/targets/04_B06-C04.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/e520a4d5-f25d-480f-aea3-35fbb6fea9e8_1930964_invisible.mp4|out/videos/targets/05_B05-C10.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/5624aaaf-dec9-460c-8adb-436852ef1832_1931100_invisible.mp4|out/videos/targets/06_B05-C05.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/6110e9d9-501f-446b-87ae-6203db8203ae_1931061_invisible.mp4|out/videos/targets/07_B05-C05.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/b018d9ca-e8c7-49a4-9b6f-f6bbae3571eb_1931081_invisible.mp4|out/videos/targets/08_B08-C08.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112113/df40cbb4-d1fd-4a8e-935c-934787e1d71d_1931088_invisible.mp4|out/videos/targets/09_B10-C06.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/f90cce08-7eb4-4b46-a4c0-f931c9dc7686_1931151_invisible.mp4|out/videos/targets/10_B02-C03.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/1f226ba4-72e2-47bb-991e-83a032f8f6f9_1931169_invisible.mp4|out/videos/targets/11_B01-C02.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/bc876a74-9855-4bb9-91c4-b4ad2c0f552e_1931215_invisible.mp4|out/videos/targets/12_B10-C02.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/247b4ffd-dc2e-4ace-957f-810aa1fc1ac5_1931182_invisible.mp4|out/videos/targets/13_B08-C04.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/ba87f0d7-b925-4065-8133-f1f0c4668c78_1931209_invisible.mp4|out/videos/targets/14_B08-C10.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/f3fe7ac3-7bad-4c61-bcea-24f0e6f1022d_1931239_invisible.mp4|out/videos/targets/15_B10-C07.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/ffb9e5d8-afb8-43b2-9760-3315b5fb7e6d_1931370_invisible.mp4|out/videos/targets/16_B01-C07.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/cdda6827-2c90-4046-bf6d-cd79aa89c5d8_1931412_invisible.mp4|out/videos/targets/17_B07-C10.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/b37d273c-ff6d-49dd-956f-caeb331b0110_1931334_invisible.mp4|out/videos/targets/18_B10-C10.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/e90510df-b640-4cb1-a5cf-ab873a3845cb_1931365_invisible.mp4|out/videos/targets/19_B10-C05.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/8725f513-1920-4eff-a5c9-fa07dfcfd6e7_1931385_invisible.mp4|out/videos/targets/20_B10-C03.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/c91e8ace-41a1-4731-80fb-c3fbacbafa20_1931440_invisible.mp4|out/videos/targets/21_B10-C04.mp4" \
  "https://dkd1gl5cnghzf.cloudfront.net/wizstar_watermark/2026112114/111ebb10-b3e2-4e93-a96e-7b09c737994a_1931459_invisible.mp4|out/videos/targets/22_case22.mp4" \
  ; do
  url="${spec%%|*}"; path="${spec#*|}"
  if curl -fSL --retry 3 --retry-delay 2 --connect-timeout 20 --max-time 300 -o "$path" "$url"; then echo "OK $path"; ok=$((ok+1)); else echo "FAIL $path $url"; fail=$((fail+1)); fi
done
echo "RESULT ok=$ok fail=$fail"
