using System;
using UnityEngine;

/// <summary>
/// Depth visualization for API capture: prefers geometry pass (off-screen safe), falls back to _CameraDepthTexture blit.
/// NOTE: Hidden shaders must be included in the player build — use Graphics Settings → Always Included Shaders,
/// or Shader.Find returns null in standalone while often working in the Editor.
/// </summary>
public static class DepthVisualizeCapture
{
    private const string ShaderNameGeometry = "Hidden/THOR_DepthFromGeometry";
    private const string ShaderNameVisualize = "Hidden/THOR_DepthVisualize";

    private static Material s_depthMaterial;

    private static Shader ResolveGeometryShader()
    {
        Shader sh = Shader.Find(ShaderNameGeometry);
        if (sh == null)
            Debug.LogError($"[{nameof(DepthVisualizeCapture)}] {ShaderNameGeometry} not found (stripped from build?). Add it under Edit → Project Settings → Graphics → Always Included Shaders.");
        return sh;
    }

    private static Material DepthMaterial
    {
        get
        {
            if (s_depthMaterial == null)
            {
                Shader sh = Shader.Find(ShaderNameVisualize);
                if (sh == null)
                {
                    Debug.LogError($"[{nameof(DepthVisualizeCapture)}] {ShaderNameVisualize} not found (stripped from build?). Add it under Graphics → Always Included Shaders.");
                    return null;
                }
                s_depthMaterial = new Material(sh) { hideFlags = HideFlags.HideAndDontSave };
            }
            return s_depthMaterial;
        }
    }

    /// <summary>Call when depth PNG is null to diagnose Editor vs Player differences.</summary>
    public static void LogDepthFailureDiagnostics(Camera camera, int width, int height)
    {
        Debug.LogError(
            $"[DepthCapture FAIL] graphicsAPI={SystemInfo.graphicsDeviceType} graphicsTier={Graphics.activeTier} " +
            $"size={width}x{height}");
        Debug.LogError(
            $"[DepthCapture FAIL] camera={(camera != null ? camera.name : "null")} " +
            $"depthTextureMode={(camera != null ? camera.depthTextureMode.ToString() : "-")}");
        Shader sg = Shader.Find(ShaderNameGeometry);
        Shader sv = Shader.Find(ShaderNameVisualize);
        Debug.LogError(
            $"[DepthCapture FAIL] Shader.Find {ShaderNameGeometry}={(sg != null)} " +
            $"{ShaderNameVisualize}={(sv != null)}");
        Debug.LogError(
            $"[DepthCapture FAIL] SupportsRenderTextureFormat ARGB32={SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGB32)} " +
            $"Depth={SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.Depth)}");
    }

    /// <summary>
    /// Second render pass: replaces materials to write normalized view depth as grayscale (works when global depth texture is empty).
    /// </summary>
    public static byte[] CaptureDepthGeometryPng(Camera camera, int width, int height)
    {
        Shader sh = ResolveGeometryShader();
        if (sh == null || camera == null || width <= 0 || height <= 0)
        {
            return null;
        }

        RenderTexture depthRt = RenderTexture.GetTemporary(width, height, 24, RenderTextureFormat.ARGB32);
        RenderTexture prevActive = RenderTexture.active;
        RenderTexture prevTarget = camera.targetTexture;
        CameraClearFlags prevClear = camera.clearFlags;
        Color prevBg = camera.backgroundColor;

        try
        {
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.targetTexture = depthRt;
            camera.RenderWithShader(sh, "RenderType");

            Texture2D tex = new Texture2D(width, height, TextureFormat.RGB24, false);
            RenderTexture.active = depthRt;
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            byte[] png = tex.EncodeToPNG();
            UnityEngine.Object.Destroy(tex);
            return png;
        }
        finally
        {
            RenderTexture.active = prevActive;
            camera.targetTexture = prevTarget;
            camera.clearFlags = prevClear;
            camera.backgroundColor = prevBg;
            RenderTexture.ReleaseTemporary(depthRt);
        }
    }

    /// <summary>
    /// Preferred entry: geometry pass, then _CameraDepthTexture blit if needed.
    /// </summary>
    public static byte[] CaptureDepthAsPng(Camera camera, int width, int height)
    {
        byte[] geom = CaptureDepthGeometryPng(camera, width, height);
        if (geom != null)
            return geom;
        return CaptureDepthVisualizationPng(camera, width, height);
    }

    /// <summary>
    /// Call after <paramref name="camera"/>.Render() with depthTextureMode set. Encodes visualization as PNG bytes.
    /// </summary>
    public static byte[] CaptureDepthVisualizationPng(Camera camera, int width, int height)
    {
        Material mat = DepthMaterial;
        if (mat == null || camera == null || width <= 0 || height <= 0)
            return null;

        RenderTexture depthVis = RenderTexture.GetTemporary(width, height, 0, RenderTextureFormat.ARGB32);
        RenderTexture prevActive = RenderTexture.active;
        try
        {
            Graphics.Blit(null, depthVis, mat);
            Texture2D tex = new Texture2D(width, height, TextureFormat.RGB24, false);
            RenderTexture.active = depthVis;
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            byte[] png = tex.EncodeToPNG();
            UnityEngine.Object.Destroy(tex);
            return png;
        }
        finally
        {
            RenderTexture.active = prevActive;
            RenderTexture.ReleaseTemporary(depthVis);
        }
    }
}
