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

    private void Awake()
    {
        try
        {
            listener = new HttpListener();
            listener.Prefixes.Add(url);
            listener.Start();
            Debug.Log("Http Listening...");
            HandleIncomingConnections();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to start HttpListener: {ex.Message}");
        }
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
                    listener.Stop();
                    listener.Close();
                }

                if (request.Url.AbsolutePath == "/v1/env/scene_reset")
                {
                    restfulApi.SceneResetApi(request, response);
                    listener.Stop();
                    listener.Close();
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
