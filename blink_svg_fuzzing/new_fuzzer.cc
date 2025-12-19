
#include "base/memory/scoped_refptr.h"
#include "base/numerics/checked_math.h"
#include "base/numerics/clamped_math.h"
#include "base/task/sequenced_task_runner.h"
#include "base/task/single_thread_task_runner.h"
#include "gpu/command_buffer/client/shared_image_interface.h"
#include "gpu/command_buffer/common/shared_image_usage.h"
#include "gpu/config/gpu_feature_info.h"
#include "skia/ext/legacy_display_globals.h"
#include "third_party/blink/public/common/features.h"
#include "third_party/blink/public/platform/platform.h"
#include "third_party/blink/public/platform/web_media_player.h"
#include "third_party/blink/renderer/bindings/core/v8/script_promise_resolver.h"
#include "third_party/blink/renderer/bindings/core/v8/to_v8_traits.h"
#include "third_party/blink/renderer/bindings/core/v8/v8_throw_dom_exception.h"
#include "third_party/blink/renderer/core/dom/dom_exception.h"
#include "third_party/blink/renderer/core/html/canvas/html_canvas_element.h"
#include "third_party/blink/renderer/core/html/canvas/image_data.h"
#include "third_party/blink/renderer/core/html/canvas/image_element_base.h"
#include "third_party/blink/renderer/core/html/media/html_video_element.h"
#include "third_party/blink/renderer/core/offscreencanvas/offscreen_canvas.h"
#include "third_party/blink/renderer/core/svg/graphics/svg_image_for_container.h"
#include "third_party/blink/renderer/platform/bindings/enumeration_base.h"
#include "third_party/blink/renderer/platform/graphics/accelerated_static_bitmap_image.h"
#include "third_party/blink/renderer/platform/graphics/canvas_resource_provider.h"
#include "third_party/blink/renderer/platform/graphics/gpu/shared_gpu_context.h"
#include "third_party/blink/renderer/platform/graphics/graphics_context.h"
#include "third_party/blink/renderer/platform/graphics/graphics_context_types.h"
#include "third_party/blink/renderer/platform/graphics/image.h"
#include "third_party/blink/renderer/platform/graphics/static_bitmap_image_transform.h"
#include "third_party/blink/renderer/platform/graphics/unaccelerated_static_bitmap_image.h"
#include "third_party/blink/renderer/platform/graphics/video_frame_image_util.h"
#include "third_party/blink/renderer/platform/heap/cross_thread_handle.h"
#include "third_party/blink/renderer/platform/heap/garbage_collected.h"
#include "third_party/blink/renderer/platform/image-decoders/image_decoder.h"
#include "third_party/blink/renderer/platform/scheduler/public/main_thread.h"
#include "third_party/blink/renderer/platform/scheduler/public/post_cross_thread_task.h"
#include "third_party/blink/renderer/platform/scheduler/public/worker_pool.h"
#include "third_party/blink/renderer/platform/transforms/affine_transform.h"
#include "third_party/blink/renderer/platform/wtf/cross_thread_copier_base.h"
#include "third_party/blink/renderer/platform/wtf/cross_thread_copier_gfx.h"
#include "third_party/blink/renderer/platform/wtf/cross_thread_copier_skia.h"
#include "third_party/blink/renderer/platform/wtf/cross_thread_copier_std.h"
#include "third_party/blink/renderer/platform/wtf/cross_thread_functional.h"
#include "third_party/skia/include/core/SkCanvas.h"
#include "third_party/skia/include/core/SkImage.h"
#include "third_party/skia/include/core/SkImageInfo.h"
#include "third_party/skia/include/core/SkSurface.h"
#include "third_party/skia/include/core/SkSwizzle.h"

// END BLOCK



#include <memory>

#include "third_party/blink/renderer/core/svg/graphics/svg_image.h"
#include "third_party/blink/renderer/core/svg/graphics/svg_image_chrome_client.h"
#include "third_party/blink/renderer/platform/testing/blink_fuzzer_test_support.h"
#include "third_party/blink/renderer/platform/testing/task_environment.h"
#include "third_party/blink/renderer/platform/wtf/shared_buffer.h"

#include "cc/paint/paint_flags.h"
#include "third_party/skia/include/core/SkCanvas.h"
#include "third_party/skia/include/utils/SkNullCanvas.h"

#include "third_party/blink/renderer/core/paint/paint_flags.h"
#include "third_party/blink/renderer/platform/graphics/image.h"
// #include "third_party/blink/renderer/platform/graphics/image_draw_options.h"
#include "ui/gfx/geometry/rect_f.h"
using namespace blink;

namespace {

// -------- Global, reused state --------

std::unique_ptr<test::TaskEnvironment> g_task_environment;

scoped_refptr<SVGImage> g_image;


// Reused paint objects
std::unique_ptr<cc::PaintRecorder> g_recorder;

// -------------------------------------

class FuzzImageObserver final
    : public GarbageCollected<FuzzImageObserver>,
      public ImageObserver {
 public:
  bool ShouldPauseAnimation(const Image*) override { return false; }
  void DecodedSizeChangedTo(const Image*, size_t) override {}
  void Changed(const Image*) override {}
  void AsyncLoadCompleted(const Image*) override {}

  void Trace(Visitor* visitor) const override {
    ImageObserver::Trace(visitor);
  }
};

void DrawOnce(Image* image) {
  cc::PaintCanvas* canvas = g_recorder->beginRecording();

  cc::PaintFlags flags;
  gfx::RectF rect(0, 0, 256, 256);

  image->Draw(canvas, flags, rect, rect, ImageDrawOptions());

  g_recorder->finishRecordingAsPicture();
}

Persistent<FuzzImageObserver> g_observer;

}  // namespace

// -------- One-time initialization --------

extern "C" int LLVMFuzzerInitialize(int* argc, char*** argv) {
  static BlinkFuzzerTestSupport blink_support;
  
  g_task_environment =
      std::make_unique<test::TaskEnvironment>(
          test::TaskEnvironment::TimeSource::MOCK_TIME);
  

  g_observer = MakeGarbageCollected<FuzzImageObserver>();
  g_image = SVGImage::Create(g_observer);

  g_recorder = std::make_unique<cc::PaintRecorder>();

  return 0;
}

// -------- Fast fuzz loop --------

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  if (size < 10 || size > (1 << 20))
    return 0;

  scoped_refptr<SharedBuffer> buffer =
      SharedBuffer::Create(base::span<const uint8_t>(data, size));

  // Only mutate data
  g_image->SetData(buffer, true);

  // Exercise rendering paths
  DrawOnce(g_image.get());

  return 0;
}