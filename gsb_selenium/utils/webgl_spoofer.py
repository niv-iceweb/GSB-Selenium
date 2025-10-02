"""WebGL Spoofer for GSB-Selenium."""

import random
from typing import Dict, List, Any


class WebGLSpoofer:
    """WebGL fingerprint spoofer focused on key properties."""
    
    # Common GPU vendors and their typical renderers
    GPU_PROFILES = [
        {
            "vendor": "Google Inc. (Intel)",
            "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "extensions": [
                "ANGLE_instanced_arrays", "EXT_blend_minmax", "EXT_color_buffer_half_float",
                "EXT_disjoint_timer_query", "EXT_float_blend", "EXT_frag_depth",
                "EXT_shader_texture_lod", "EXT_texture_compression_bptc", "EXT_texture_compression_rgtc",
                "EXT_texture_filter_anisotropic", "WEBKIT_EXT_texture_filter_anisotropic",
                "EXT_sRGB", "OES_element_index_uint", "OES_fbo_render_mipmap",
                "OES_standard_derivatives", "OES_texture_float", "OES_texture_float_linear",
                "OES_texture_half_float", "OES_texture_half_float_linear", "OES_vertex_array_object",
                "WEBGL_color_buffer_float", "WEBGL_compressed_texture_s3tc",
                "WEBKIT_WEBGL_compressed_texture_s3tc", "WEBGL_compressed_texture_s3tc_srgb",
                "WEBGL_debug_renderer_info", "WEBGL_debug_shaders", "WEBGL_depth_texture",
                "WEBKIT_WEBGL_depth_texture", "WEBGL_draw_buffers", "WEBGL_lose_context",
                "WEBKIT_WEBGL_lose_context"
            ]
        },
        {
            "vendor": "Google Inc. (NVIDIA)",
            "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11-27.21.14.5671)",
            "extensions": [
                "ANGLE_instanced_arrays", "EXT_blend_minmax", "EXT_color_buffer_half_float",
                "EXT_disjoint_timer_query", "EXT_float_blend", "EXT_frag_depth",
                "EXT_shader_texture_lod", "EXT_texture_compression_bptc", "EXT_texture_compression_rgtc",
                "EXT_texture_filter_anisotropic", "WEBKIT_EXT_texture_filter_anisotropic",
                "EXT_sRGB", "OES_element_index_uint", "OES_fbo_render_mipmap",
                "OES_standard_derivatives", "OES_texture_float", "OES_texture_float_linear",
                "OES_texture_half_float", "OES_texture_half_float_linear", "OES_vertex_array_object",
                "WEBGL_color_buffer_float", "WEBGL_compressed_texture_s3tc",
                "WEBKIT_WEBGL_compressed_texture_s3tc", "WEBGL_compressed_texture_s3tc_srgb",
                "WEBGL_debug_renderer_info", "WEBGL_debug_shaders", "WEBGL_depth_texture",
                "WEBKIT_WEBGL_depth_texture", "WEBGL_draw_buffers", "WEBGL_lose_context",
                "WEBKIT_WEBGL_lose_context"
            ]
        },
        {
            "vendor": "Google Inc. (AMD)",
            "renderer": "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.13025.1000)",
            "extensions": [
                "ANGLE_instanced_arrays", "EXT_blend_minmax", "EXT_color_buffer_half_float",
                "EXT_disjoint_timer_query", "EXT_float_blend", "EXT_frag_depth",
                "EXT_shader_texture_lod", "EXT_texture_compression_bptc", "EXT_texture_compression_rgtc",
                "EXT_texture_filter_anisotropic", "WEBKIT_EXT_texture_filter_anisotropic",
                "EXT_sRGB", "OES_element_index_uint", "OES_fbo_render_mipmap",
                "OES_standard_derivatives", "OES_texture_float", "OES_texture_float_linear",
                "OES_texture_half_float", "OES_texture_half_float_linear", "OES_vertex_array_object",
                "WEBGL_color_buffer_float", "WEBGL_compressed_texture_s3tc",
                "WEBKIT_WEBGL_compressed_texture_s3tc", "WEBGL_compressed_texture_s3tc_srgb",
                "WEBGL_debug_renderer_info", "WEBGL_debug_shaders", "WEBGL_depth_texture",
                "WEBKIT_WEBGL_depth_texture", "WEBGL_draw_buffers", "WEBGL_lose_context",
                "WEBKIT_WEBGL_lose_context"
            ]
        }
    ]
    
    def __init__(self):
        """Initialize the WebGL spoofer with a random profile."""
        self.profile = random.choice(self.GPU_PROFILES)
        
    def get_webgl_script(self) -> str:
        """Generate the WebGL spoofing JavaScript."""
        extensions_js = str(self.profile["extensions"]).replace("'", '"')
        
        script = f"""
(function() {{
    'use strict';
    
    // Override WebGL properties for WebGLRenderingContext
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        if (parameter === 37445) {{ // VENDOR
            return '{self.profile["vendor"]}';
        }}
        if (parameter === 37446) {{ // RENDERER
            return '{self.profile["renderer"]}';
        }}
        if (parameter === 7938) {{ // VERSION
            return 'WebGL 1.0 (OpenGL ES 2.0 Chromium)';
        }}
        if (parameter === 35724) {{ // SHADING_LANGUAGE_VERSION
            return 'WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)';
        }}
        return getParameter.call(this, parameter);
    }};
    
    const getSupportedExtensions = WebGLRenderingContext.prototype.getSupportedExtensions;
    WebGLRenderingContext.prototype.getSupportedExtensions = function() {{
        return {extensions_js};
    }};
    
    // Also override WebGL2 if available
    if (window.WebGL2RenderingContext) {{
        const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) return '{self.profile["vendor"]}';
            if (parameter === 37446) return '{self.profile["renderer"]}';
            if (parameter === 7938) return 'WebGL 2.0 (OpenGL ES 3.0 Chromium)';
            if (parameter === 35724) return 'WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)';
            return getParameter2.call(this, parameter);
        }};
        
        const getSupportedExtensions2 = WebGL2RenderingContext.prototype.getSupportedExtensions;
        WebGL2RenderingContext.prototype.getSupportedExtensions = function() {{
            return {extensions_js};
        }};
    }}
    
    // Hide webdriver property
    Object.defineProperty(navigator, 'webdriver', {{
        get: () => false,
        configurable: true
    }});
    
    console.log('WebGL spoofing active:', {{
        vendor: '{self.profile["vendor"]}',
        renderer: '{self.profile["renderer"]}',
        extensions: {len(self.profile["extensions"])} + ' extensions'
    }});
}})();
"""
        return script
        
    def get_profile_info(self) -> Dict[str, Any]:
        """Get information about the current WebGL profile."""
        return {
            "vendor": self.profile["vendor"],
            "renderer": self.profile["renderer"],
            "extensions_count": len(self.profile["extensions"]),
            "extensions": self.profile["extensions"][:5]  # First 5 for brevity
        }