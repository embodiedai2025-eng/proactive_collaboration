using UnityEngine;
using System;
using System.IO;
using System.Net;
using UnityEngine.AI;
using System.Linq;
using UnityEngine.UI;
using static OVRInput;

public class GameInitializer : MonoBehaviour
{
    
    public static HttpListener listener;
    public static string url = "http://127.0.0.1:1212/";
    private static GameInitializer instance;
    private static bool urlConfigured;
    private static string configuredUrl = "";

    [Header("Runtime URL Config")]
    [SerializeField] private bool inputUrlFromWindow = true;
    [SerializeField] private string defaultUrl = "http://127.0.0.1:1212/";
    [SerializeField] private bool stopListenerAfterSceneChange = false;

    private bool showUrlInputWindow = false;
    private string inputUrl = "";
    private string startupError = "";

    private void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }

        instance = this;
        DontDestroyOnLoad(gameObject);

        inputUrl = string.IsNullOrWhiteSpace(configuredUrl) ? defaultUrl : configuredUrl;

        if (urlConfigured)
        {
            showUrlInputWindow = false;
            if (listener == null || !listener.IsListening)
            {
                StartHttpListener(configuredUrl);
            }
            return;
        }

        // Headless/server mode: no GUI input is available. Resolve URL from args/env first.
        if (Application.isBatchMode)
        {
            if (TryResolveHeadlessListenerUrl(out string headlessUrl, out string headlessError))
            {
                configuredUrl = headlessUrl;
                urlConfigured = true;
                showUrlInputWindow = false;
                StartHttpListener(headlessUrl);
                return;
            }

            startupError = headlessError;
            Debug.LogError("Headless URL resolution failed: " + headlessError);
            return;
        }

        if (inputUrlFromWindow)
        {
            showUrlInputWindow = true;
            return;
        }

        if (!TryNormalizeListenerUrl(defaultUrl, out string normalizedUrl, out string error))
        {
            startupError = error;
            showUrlInputWindow = true;
            return;
        }

        configuredUrl = normalizedUrl;
        urlConfigured = true;
        StartHttpListener(normalizedUrl);
    }

    private void OnGUI()
    {
        if (!showUrlInputWindow)
        {
            return;
        }

        float width = 620f;
        float height = 170f;
        Rect rect = new Rect((Screen.width - width) / 2f, (Screen.height - height) / 2f, width, height);
        GUI.Box(rect, "HTTP Listener URL");

        GUILayout.BeginArea(new Rect(rect.x + 20f, rect.y + 35f, rect.width - 40f, rect.height - 45f));
        GUILayout.Label("Input URL (must include http:// and trailing /):");
        inputUrl = GUILayout.TextField(inputUrl, 200);

        GUILayout.Space(8f);
        GUILayout.BeginHorizontal();
        if (GUILayout.Button("Start", GUILayout.Height(30f)))
        {
            if (!TryNormalizeListenerUrl(inputUrl, out string normalizedUrl, out string error))
            {
                startupError = error;
            }
            else
            {
                startupError = string.Empty;
                configuredUrl = normalizedUrl;
                urlConfigured = true;
                showUrlInputWindow = false;
                StartHttpListener(normalizedUrl);
            }
        }

        if (GUILayout.Button("Use Default", GUILayout.Height(30f)))
        {
            inputUrl = defaultUrl;
        }
        GUILayout.EndHorizontal();

        if (!string.IsNullOrEmpty(startupError))
        {
            GUILayout.Space(6f);
            GUILayout.Label("Error: " + startupError);
        }
        GUILayout.EndArea();
    }

    private void StartHttpListener(string listenerUrl)
    {
        try
        {
            if (listener != null && listener.IsListening)
            {
                return;
            }

            url = listenerUrl;
            listener = new HttpListener();
            listener.Prefixes.Add(url);
            listener.Start();
            Debug.Log($"Http Listening on {url}");
            HandleIncomingConnections();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to start HttpListener: {ex.Message}");
            startupError = ex.Message;
            urlConfigured = false;
            showUrlInputWindow = inputUrlFromWindow;
        }
    }

    private void OnApplicationQuit()
    {
        if (listener != null)
        {
            try
            {
                listener.Stop();
                listener.Close();
            }
            catch (Exception)
            {
                // Ignore cleanup exceptions during app quit.
            }
        }
    }

    private bool TryNormalizeListenerUrl(string rawUrl, out string normalizedUrl, out string error)
    {
        normalizedUrl = string.Empty;
        error = string.Empty;

        if (string.IsNullOrWhiteSpace(rawUrl))
        {
            error = "URL cannot be empty.";
            return false;
        }

        string trimmed = rawUrl.Trim();

        if (!trimmed.StartsWith("http://", StringComparison.OrdinalIgnoreCase))
        {
            error = "Only http:// URL is supported by HttpListener in this setup.";
            return false;
        }

        if (!trimmed.EndsWith("/"))
        {
            trimmed += "/";
        }

        if (!Uri.TryCreate(trimmed, UriKind.Absolute, out Uri uri))
        {
            error = "Invalid URL format.";
            return false;
        }

        if (uri.Scheme != Uri.UriSchemeHttp)
        {
            error = "Only http scheme is supported.";
            return false;
        }

        normalizedUrl = uri.ToString();
        return true;
    }

    private bool TryResolveHeadlessListenerUrl(out string normalizedUrl, out string error)
    {
        normalizedUrl = string.Empty;
        error = string.Empty;

        // Priority:
        // 1) --http-url
        // 2) --http-port
        // 3) THOR_HTTP_URL
        // 4) THOR_HTTP_PORT
        // 5) defaultUrl
        if (TryGetCommandLineValue("--http-url", out string cliUrl))
        {
            if (TryNormalizeListenerUrl(cliUrl, out normalizedUrl, out error))
            {
                return true;
            }
            error = "Invalid --http-url: " + error;
            return false;
        }

        if (TryGetCommandLineValue("--http-port", out string cliPort))
        {
            if (!int.TryParse(cliPort, out int cliPortValue) || cliPortValue <= 0 || cliPortValue > 65535)
            {
                error = "Invalid --http-port. Expected 1-65535.";
                return false;
            }

            if (TryNormalizeListenerUrl(BuildUrlFromPort(cliPortValue), out normalizedUrl, out error))
            {
                return true;
            }
            error = "Failed to normalize URL from --http-port: " + error;
            return false;
        }

        string envUrl = Environment.GetEnvironmentVariable("THOR_HTTP_URL");
        if (!string.IsNullOrWhiteSpace(envUrl))
        {
            if (TryNormalizeListenerUrl(envUrl, out normalizedUrl, out error))
            {
                return true;
            }
            error = "Invalid THOR_HTTP_URL: " + error;
            return false;
        }

        string envPort = Environment.GetEnvironmentVariable("THOR_HTTP_PORT");
        if (!string.IsNullOrWhiteSpace(envPort))
        {
            if (!int.TryParse(envPort, out int envPortValue) || envPortValue <= 0 || envPortValue > 65535)
            {
                error = "Invalid THOR_HTTP_PORT. Expected 1-65535.";
                return false;
            }

            if (TryNormalizeListenerUrl(BuildUrlFromPort(envPortValue), out normalizedUrl, out error))
            {
                return true;
            }
            error = "Failed to normalize URL from THOR_HTTP_PORT: " + error;
            return false;
        }

        if (TryNormalizeListenerUrl(defaultUrl, out normalizedUrl, out error))
        {
            return true;
        }
        error = "Invalid defaultUrl in headless mode: " + error;
        return false;
    }

    private static string BuildUrlFromPort(int port)
    {
        // For headless/container deployments, 0.0.0.0 is typically preferred.
        return "http://0.0.0.0:" + port + "/";
    }

    private static bool TryGetCommandLineValue(string key, out string value)
    {
        value = string.Empty;
        string[] args = Environment.GetCommandLineArgs();
        if (args == null || args.Length == 0)
        {
            return false;
        }

        for (int i = 0; i < args.Length; i++)
        {
            string arg = args[i];
            if (string.IsNullOrWhiteSpace(arg))
            {
                continue;
            }

            // --key=value
            string prefix = key + "=";
            if (arg.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
            {
                value = arg.Substring(prefix.Length).Trim();
                return !string.IsNullOrWhiteSpace(value);
            }

            // --key value
            if (string.Equals(arg, key, StringComparison.OrdinalIgnoreCase))
            {
                if (i + 1 < args.Length)
                {
                    value = args[i + 1].Trim();
                    return !string.IsNullOrWhiteSpace(value);
                }
                return false;
            }
        }

        return false;
    }

    
    



    

    
    



    




















































    public async void HandleIncomingConnections()
    {
        RestfulApiManagement restfulApi = gameObject.GetComponent<RestfulApiManagement>();
        if (restfulApi == null)
        {
            Debug.LogError("RestfulApiManagement component not found on the GameObject.");
            return;
        }
        bool runServer = true;
        while (runServer)
        {
            if (!listener.IsListening)
            {
                Debug.Log("HttpListener is no longer listening. Exiting loop.");
                break;
            }
            HttpListenerContext ctx = await listener.GetContextAsync();
            HttpListenerRequest request = ctx.Request;
            HttpListenerResponse response = ctx.Response;
                
            if (request.HttpMethod == "POST")
            {
                
                if (request.Url.AbsolutePath == "/shut_down")
                {
                    Debug.Log("########### Server SHUTDOWN ###############");
                    runServer = false;
                }
                
                if (request.Url.AbsolutePath == "/v1/env/select_scene")
                {
                    restfulApi.SelectSceneApi(request, response);
                    if (stopListenerAfterSceneChange)
                    {
                        listener.Stop();
                        listener.Close();
                    }
                }
                
                if (request.Url.AbsolutePath == "/v1/env/scene_reset")
                {
                    restfulApi.SceneResetApi(request, response);
                    if (stopListenerAfterSceneChange)
                    {
                        listener.Stop();
                        listener.Close();
                    }
                }
                
                if (request.Url.AbsolutePath == "/v1/env/pause")
                {
                    restfulApi.GamePauseApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/env/resume")
                {
                    restfulApi.GameResumeApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/info/get_communication_status")
                {
                    restfulApi.GetCommunicationStatusApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/env/robot_setup")
                {
                    restfulApi.RobotsSetup(request, response);
                    
                }
                
                if (request.Url.AbsolutePath == "/v1/info/get_object_info")
                {
                    restfulApi.GetObjInfo(request, response);
                }
                if (request.Url.AbsolutePath == "/v1/info/get_object_neighbors")
                {
                    restfulApi.GetObjNeighbors(request, response);
                }
                
                if (request.Url.AbsolutePath == "/select_task_type")
                {

                }
                
                if (request.Url.AbsolutePath == "/v1/info/get_robot_rgbd")
                {
                    restfulApi.GetRobotsRgbdApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/info/get_reachable_points")
                {
                    restfulApi.GetReachablePointsApi(request, response);
                }
                
                



                if (request.Url.AbsolutePath == "/v1/info/robot_status")
                {
                    restfulApi.GetRobotStatus(request, response);
                }
                if (request.Url.AbsolutePath == "/v1/info/object_type")
                {
                    restfulApi.GetObjectType(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/agent/robot_move")
                {
                    restfulApi.RobotMoveApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/agent/robot_rotate")
                {
                    restfulApi.RobotRotateApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/agent/robot_teleport")
                {
                    restfulApi.RobotsTeleportApi(request, response);
                }
                
                




                
                if (request.Url.AbsolutePath == "/v1/agent/pick")
                {
                    restfulApi.RobotPickApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/agent/place")
                {
                    restfulApi.RobotPlaceApi(request, response);
                }
                if (request.Url.AbsolutePath == "/v1/agent/pull")
                {
                    restfulApi.RobotPullApi(request, response);
                }
                if (request.Url.AbsolutePath == "/v1/agent/joint_pull")
                {
                    restfulApi.RobotJointPullApi(request, response);
                }

                if (request.Url.AbsolutePath == "/v1/env/get_obs")
                {
                    restfulApi.GetRobotsObs(request, response);
                }

                if (request.Url.AbsolutePath == "/v1/env/get_topdown_image")
                {
                    restfulApi.GetTopdownDisplayImageApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/env/add_object")
                {
                    restfulApi.ObjectsAddApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/env/move_object")
                {
                    restfulApi.ObjectsTeleportApi(request, response);
                }
                
                if (request.Url.AbsolutePath == "/v1/env/disable_object")
                {
                    restfulApi.ObjectsDeleteApi(request, response);
                }
                if (request.Url.AbsolutePath == "/v1/info/is_object_in_view")
                {
                    restfulApi.IsObjectInViewApi(request, response);
                }
            }
     
        }
    }

  









































   











    








































































   














}
