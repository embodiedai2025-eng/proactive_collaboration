// Replaces surface shaders during Camera.RenderWithShader: encodes view-space depth as grayscale.
// Works for off-screen RenderTexture where _CameraDepthTexture blit is often empty (all black).

Shader "Hidden/THOR_DepthFromGeometry"
{
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        Pass
        {
            Name "THORDEPTH"
            ZWrite On
            ZTest LEqual
            Cull Back

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float depth01 : TEXCOORD0;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                float3 vpos = UnityObjectToViewPos(v.vertex);
                float viewZ = -vpos.z;
                float n = _ProjectionParams.y;
                float f = _ProjectionParams.z;
                float denom = max(f - n, 1e-5);
                o.depth01 = saturate((viewZ - n) / denom);
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                return fixed4(i.depth01, i.depth01, i.depth01, 1.0);
            }
            ENDCG
        }
    }

    SubShader { Tags { "RenderType"="AlphaTest" } UsePass "Hidden/THOR_DepthFromGeometry/THORDEPTH" }
    SubShader { Tags { "RenderType"="TransparentCutout" } UsePass "Hidden/THOR_DepthFromGeometry/THORDEPTH" }
    SubShader { Tags { "RenderType"="TreeOpaque" } UsePass "Hidden/THOR_DepthFromGeometry/THORDEPTH" }
    SubShader { Tags { "RenderType"="TreeTransparentCutout" } UsePass "Hidden/THOR_DepthFromGeometry/THORDEPTH" }
    SubShader { Tags { "RenderType"="Background" } UsePass "Hidden/THOR_DepthFromGeometry/THORDEPTH" }

    FallBack Off
}
