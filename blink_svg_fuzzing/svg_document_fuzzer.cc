/*

// svg_document_fuzzer.cc
#include "third_party/blink/renderer/core/xml/dom_parser.h"
#include "third_party/blink/renderer/platform/testing/blink_fuzzer_test_support.h"
#include "base/test/metrics/histogram_tester.h"
#include "testing/gtest/include/gtest/gtest.h"
#include "third_party/blink/renderer/bindings/core/v8/v8_binding_for_testing.h"
#include "third_party/blink/renderer/bindings/core/v8/v8_supported_type.h"
#include "third_party/blink/renderer/core/dom/document_fragment.h"
#include "third_party/blink/renderer/core/dom/text.h"
#include "third_party/blink/renderer/core/editing/serializers/serialization.h"
#include "third_party/blink/renderer/core/html/forms/form_controller.h"
#include "third_party/blink/renderer/core/html/forms/html_input_element.h"
#include "third_party/blink/renderer/core/html/forms/html_text_area_element.h"
#include "third_party/blink/renderer/core/html/html_body_element.h"
#include "third_party/blink/renderer/core/html/html_div_element.h"
#include "third_party/blink/renderer/core/html/html_document.h"
#include "third_party/blink/renderer/core/html/parser/html_construction_site.h"
#include "third_party/blink/renderer/core/keywords.h"
#include "third_party/blink/renderer/core/style/computed_style.h"
#include "third_party/blink/renderer/core/testing/null_execution_context.h"
#include "third_party/blink/renderer/core/xml/dom_parser.h"
#include "third_party/blink/renderer/platform/testing/task_environment.h"
#include "third_party/blink/renderer/platform/wtf/text/string_builder.h"

// Not needed anymore ... #include "third_party/blink/renderer/core/testing/dummy_page_holder.h" // Contains the stuff for DummyPageHolder

// These two next includes are for the v8 setup...

#include "v8/include/libplatform/libplatform.h"
#include "v8/include/v8.h"

extern "C" int LLVMFuzzerInitialize(int* argc, char*** argv) {
  static blink::BlinkFuzzerTestSupport test_support = blink::BlinkFuzzerTestSupport(); // Create fuzzer test support here.
  // Taken from run_all_unittests.cc
  // mojo::core::Init(); // Not needed I think
  v8::V8::InitializeICUDefaultLocation(*argv[0]);
  v8::V8::InitializeExternalStartupData(*argv[0]);
  auto platform = v8::platform::NewDefaultPlatform();
  v8::V8::InitializePlatform(platform.get());
  v8::V8::Initialize();
  return 0; // Return success...
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  // These next two things do not work for some reason.
  // static base::test::SingleThreadTaskEnvironment task_environment;
  // base::test::TaskEnvironment task_environment;
  String svg_input = String::FromUTF8WithLatin1Fallback(UNSAFE_BUFFERS({data, size}));
  blink::V8TestingScope scope;
  auto* parser = blink::DOMParser::Create(scope.GetScriptState());
  parser->parseFromString(svg_input, blink::V8SupportedType(blink::V8SupportedType::Enum::kImageSvgXml)); // Load svg image...
  return 0;
}

*/


// This block of includes is taken from image_bitmap.cc:

// START BLOCK

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

/*
void DrawOnce(Image* image) {
  std::unique_ptr<SkCanvas> null_canvas = SkMakeNullCanvas();
  cc::SkiaPaintCanvas canvas(null_canvas.get());
  cc::PaintFlags flags;
  gfx::RectF rect(0, 0, 256, 256);
  image->Draw(&canvas, flags, rect, rect, ImageDrawOptions());
}
*/

void DrawOnce(Image* image) {
  cc::PaintRecorder recorder;
  cc::PaintCanvas* canvas = recorder.beginRecording();

  cc::PaintFlags flags;
  gfx::RectF rect(0, 0, 256, 256);

  image->Draw(
      canvas,
      flags,
      rect,
      rect,
      ImageDrawOptions());

  // Optional: force materialization
  recorder.finishRecordingAsPicture();
}


}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  if (size < 10 || size > 1 << 20)
    return 0;

  static BlinkFuzzerTestSupport test_support;
  test::TaskEnvironment task_environment;

  auto observer = MakeGarbageCollected<FuzzImageObserver>();
  scoped_refptr<SVGImage> image = SVGImage::Create(observer);

  scoped_refptr<SharedBuffer> buffer = SharedBuffer::Create(
      base::span<const uint8_t>(data, size));

  image->SetData(buffer, true);
  // test::RunPendingTasks();

  // Force paint paths
  DrawOnce(image.get());
  DrawOnce(image.get());

  return 0;
}
