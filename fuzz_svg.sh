
ASAN_OPTIONS=external_symbolizer_path=/usr/bin/llvm-symbolizer:alloc_dealloc_mismatch=0:allocator_may_return_null=1:halt_on_error=1:abort_on_error=1 SLOT_INDEX=1 LIBFUZZER_PYTHON_MODULE=daemon PYTHONPATH=. ./canvas_fuzzer -fork=1 -max_len=20000 -ignore_crashes=1 -jobs=1 -timeout=1 -rss_limit_mb=2000 svg/

