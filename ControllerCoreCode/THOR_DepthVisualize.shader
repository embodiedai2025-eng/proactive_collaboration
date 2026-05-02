Shader "Hidden/THOR_DepthVisualize"
{
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        Pass
        {
            ZTest Always
            ZWrite Off
            Cull Off

            CGPROGRAM
            #pragma vertex vert_img
            #pragma fragment frag
            #include "UnityCG.cginc"

            // Use tex2D instead of SAMPLE_DEPTH_TEXTURE: on Vulkan/glcore the latter expands to
            // sampler_CameraDepthTexture, which is not declared when using sampler2D-only syntax.
            sampler2D _CameraDepthTexture;

            fixed4 frag(v2f_img i) : SV_Target
            {
                float d = UNITY_SAMPLE_DEPTH(tex2D(_CameraDepthTexture, i.uv));
                float lin01 = Linear01Depth(d);
                return fixed4(lin01, lin01, lin01, 1.0);
            }
            ENDCG
        }
    }
    FallBack Off
}
