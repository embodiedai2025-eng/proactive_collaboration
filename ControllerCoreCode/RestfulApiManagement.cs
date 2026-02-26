using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Linq;

public class RestfulApiManagement : MonoBehaviour
{

    public void SelectSceneApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Select Scene");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            Dictionary<string, object> ScenceDict = ToDict(request);
            int SenceIndex = Convert.ToInt32(ScenceDict["scene_id"]);
            Debug.Log(SenceIndex);
            GameObject sceneSwitcherObject = GameObject.Find("getObj");
            EnvController envController = sceneSwitcherObject.GetComponent<EnvController>(); ;
            envController.SelectScene(SenceIndex);
            jsonResponse = JsonConvert.SerializeObject(new { success = true, message = "null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void SceneResetApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Scene Reset");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            GameObject gamePauseObject = GameObject.Find("getObj");
            EnvController envController = gamePauseObject.GetComponent<EnvController>(); ;
            envController.SceneReset();
            jsonResponse = JsonConvert.SerializeObject(new { success = true, message = "null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void GamePauseApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Game Pause");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            GameObject gamePauseObject = GameObject.Find("getObj");
            EnvController envController = gamePauseObject.GetComponent<EnvController>(); ;
            envController.GamePasue();
            jsonResponse = JsonConvert.SerializeObject(new { success = true, message = "null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void GameResumeApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Game Resume");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            GameObject gamePauseObject = GameObject.Find("getObj");
            EnvController envController = gamePauseObject.GetComponent<EnvController>(); ;
            envController.GameResume();
            jsonResponse = JsonConvert.SerializeObject(new { success = true, message = "null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void RobotsSetup(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Robots setup");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";
        try
        {

            Dictionary<string, object> robotSetupDict = ToDict(request);
            GameObject getObj = GameObject.Find("getObj");
            EnvController envController = getObj.GetComponent<EnvController>();

            HashSet<string> validRobotNames = new HashSet<string>();

            foreach (var entry in robotSetupDict)
            {
                Dictionary<string, object> singleRobot = ObjToDict(entry.Value);
                string singleRobotType = singleRobot["type"].ToString();
                string singleRobotName = singleRobot["name"].ToString();

                validRobotNames.Add(singleRobotName);

                string armLength = singleRobot.ContainsKey("arm_length") ? singleRobot["arm_length"].ToString() : "0.7"; 
                string strength = singleRobot.ContainsKey("strength") ? singleRobot["strength"].ToString() : "50";
                string robotLow = singleRobot.ContainsKey("robot_low") ? singleRobot["robot_low"].ToString() : "0";
                string robotHigh = singleRobot.ContainsKey("robot_high") ? singleRobot["robot_high"].ToString() : "1";

                Vector3 singleRobotPosition = ParseVector3(singleRobot["init_location"]);
                Vector3 singleRobotRotation = ParseVector3(singleRobot["init_rotation"]);
                envController.SingleRobotSetup(singleRobotType, singleRobotName, singleRobotPosition, singleRobotRotation, armLength, strength, robotLow, robotHigh);
            }

            RemoveUnusedRobots(validRobotNames);

            jsonResponse = JsonConvert.SerializeObject(new { success = true, message = "null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    private void RemoveUnusedRobots(HashSet<string> validRobotNames)
    {
        GameObject[] allGameObjects = GameObject.FindObjectsOfType<GameObject>();

        foreach (var obj in allGameObjects)
        {
            if (obj.name.StartsWith("Robot_") && !validRobotNames.Contains(obj.name))
            {
                Debug.Log($"Removing unused robot: {obj.name}");
                GameObject.Destroy(obj);
            }
        }
    }
    public void RobotMoveApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Robot Move");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            Dictionary<string, object> robotSetupDict = ToDict(request);
            foreach (var entry in robotSetupDict)
            {
                string singleRobotName = entry.Key;
                Debug.Log("singleRobotName" + singleRobotName);
                Dictionary<string, object> singleRobotProperty = ObjToDict(entry.Value);
                Vector2 singleRobotMagnitude = ParseVector2(singleRobotProperty["magnitude"]);
                float singleRobotSpeed = float.Parse(singleRobotProperty["speed"].ToString());
                GameObject robot = GameObject.Find(singleRobotName);
                RobotController robotController = robot.GetComponent<RobotController>();
                if (robotController != null)
                {
                    robotController.Move(singleRobotMagnitude, singleRobotSpeed);
                }
                else
                {
                    Debug.LogWarning($"Robot with name {singleRobotName} not found.");
                }
            }
            jsonResponse = JsonConvert.SerializeObject(new { success = true, message = "Move success" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }
    public void RobotRotateApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Robot Rotate");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            Dictionary<string, object> robotSetupDict = ToDict(request);
            foreach (var entry in robotSetupDict)
            {
                string singleRobotName = entry.Key;
                Dictionary<string, object> singleRobotProperty = ObjToDict(entry.Value);
                float singleRobotRotate = float.Parse(singleRobotProperty["angle"].ToString());
                GameObject robot = GameObject.Find(singleRobotName);
                RobotController robotController = robot.GetComponent<RobotController>();
                if (robotController != null)
                {
                    robotController.Rotate(singleRobotRotate);
                }
                else
                {
                    Debug.LogWarning($"Robot with name {singleRobotName} not found.");
                }
            }
            jsonResponse = JsonConvert.SerializeObject(new { success = true, message = "Move success" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void RobotsTeleportApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Robots teleport");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try 
        {

            Dictionary<string, object> robotsTeleport = ToDict(request);

            foreach (var entry in robotsTeleport)
            {
                string robotName = entry.Key;
                Dictionary<string, object> robotData = ObjToDict(entry.Value);
                Vector3 targetPosition = ParseVector3(robotData["location"]);
                Vector3 targetRotation = ParseVector3(robotData["rotation"]);

                GameObject robot = GameObject.Find(robotName);
                Debug.Log("robot" + robot);
                RobotController robotController = robot.GetComponent<RobotController>();
                if (robotController != null)
                {
                    robotController.Teleport(targetPosition, targetRotation);
                }
                else
                {
                    Debug.LogWarning($"Robot with name {robotName} not found.");
                }
            }
            jsonResponse = JsonConvert.SerializeObject(new { is_success = true, error_info = "Null" }) ;
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void GetObjInfo(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get Object Info");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            Dictionary<string, object> GetObjInfoDict = ToDict(request);
            Debug.Log("GetObjInfoDict:" + GetObjInfoDict);
            GameObject robot = GameObject.Find("getObj");
            ObjectController objectController = robot.GetComponent<ObjectController>();
            JArray jArray = GetObjInfoDict["object_list"] as JArray;
            List<string> objectList = jArray.ToObject<List<string>>();

            Dictionary<string, Dictionary<string, List<float>>> responseJson = objectController.GetObjInfo(objectList);
            jsonResponse = JsonConvert.SerializeObject(responseJson, Formatting.Indented);

            JObject jsonObject = JObject.Parse(jsonResponse);

            jsonObject.Add("is_success", true);
            jsonObject.Add("error_info", "Null");
            jsonResponse = JsonConvert.SerializeObject(jsonObject, Formatting.Indented);
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { is_success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void GetObjNeighbors(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get Object Neighbors");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";

        try
        {

            Dictionary<string, object> GetObjInfoDict = ToDict(request);
            Debug.Log("GetObjInfoDict: " + GetObjInfoDict);

            if (GetObjInfoDict == null || !GetObjInfoDict.ContainsKey("object_list"))
            {
                throw new ArgumentException("Missing or invalid 'object_list' in the request.");
            }

            JArray jArray = GetObjInfoDict["object_list"] as JArray;
            if (jArray == null)
            {
                throw new ArgumentException("'object_list' must be a valid JArray.");
            }

            List<string> objectList = jArray.ToObject<List<string>>();

            GameObject robot = GameObject.Find("getObj");
            if (robot == null)
            {
                throw new Exception("Robot object 'getObj' not found in the scene.");
            }

            ObjectController objectController = robot.GetComponent<ObjectController>();
            if (objectController == null)
            {
                throw new Exception("ObjectController component not found on the 'getObj' GameObject.");
            }

            Dictionary<string, Dictionary<string, string>> responseJson = objectController.GetObjNeighbors(objectList);

            jsonResponse = JsonConvert.SerializeObject(responseJson, Formatting.Indented);

            JObject jsonObject = JObject.Parse(jsonResponse);
            jsonObject.Add("is_success", true);
            jsonObject.Add("error_info", "Null");

            jsonResponse = JsonConvert.SerializeObject(jsonObject, Formatting.Indented);
        }
        catch (Exception ex)
        {

            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { is_success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }

        SendResponse(response, jsonResponse, statusCode);
    }

    public void GetRobotStatus(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get Robot IsHold");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";

        try
        {

            Dictionary<string, object> GetObjInfoDict = ToDict(request);
            Debug.Log("GetObjInfoDict: " + GetObjInfoDict);

            if (GetObjInfoDict == null || !GetObjInfoDict.ContainsKey("robot_list"))
            {
                throw new ArgumentException("Missing or invalid 'robot_list' in the request.");
            }

            JArray jArray = GetObjInfoDict["robot_list"] as JArray;
            if (jArray == null)
            {
                throw new ArgumentException("'robot_list' must be a valid JArray.");
            }

            List<string> objectList = jArray.ToObject<List<string>>();
            Debug.Log("objectList: " + objectList[0]);

            GameObject robot = GameObject.Find("getObj");
            if (robot == null)
            {
                throw new Exception("Robot object 'getObj' not found in the scene.");
            }

            ObjectController objController = robot.GetComponent<ObjectController>();
            if (objController == null)
            {
                throw new Exception("objController component not found on the 'getObj' GameObject.");
            }

            Dictionary<string, Dictionary<string, string>> responseJson = objController.GetRobotStatus(objectList);

            jsonResponse = JsonConvert.SerializeObject(responseJson, Formatting.Indented);

            JObject jsonObject = JObject.Parse(jsonResponse);
            jsonObject.Add("is_success", true);
            jsonObject.Add("error_info", "Null");

            jsonResponse = JsonConvert.SerializeObject(jsonObject, Formatting.Indented);
        }
        catch (Exception ex)
        {

            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { is_success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }

        SendResponse(response, jsonResponse, statusCode);
    }

    public void GetObjectType(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get ObjectType");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";

        try
        {

            Dictionary<string, object> GetObjInfoDict = ToDict(request);
            Debug.Log("GetObjInfoDict: " + GetObjInfoDict);

            if (GetObjInfoDict == null || !GetObjInfoDict.ContainsKey("object_list"))
            {
                throw new ArgumentException("Missing or invalid 'object_list' in the request.");
            }

            JArray jArray = GetObjInfoDict["object_list"] as JArray;
            if (jArray == null)
            {
                throw new ArgumentException("'object_list' must be a valid JArray.");
            }

            List<string> objectList = jArray.ToObject<List<string>>();

            GameObject robot = GameObject.Find("getObj");
            if (robot == null)
            {
                throw new Exception("Robot object 'getObj' not found in the scene.");
            }

            ObjectController objController = robot.GetComponent<ObjectController>();
            if (objController == null)
            {
                throw new Exception("objController component not found on the 'getObj' GameObject.");
            }

            Dictionary<string, string> responseJson;
            try
            {
                responseJson = objController.GetObjectType(objectList);
            }
            catch (Exception ex)
            {
                throw new Exception("Error occurred while fetching object type: " + ex.Message);
            }

            JObject jsonObject = JObject.FromObject(new { data = responseJson, is_success = true, error_info = "Null" });

            jsonResponse = JsonConvert.SerializeObject(jsonObject, Formatting.Indented);
        }
        catch (Exception ex)
        {

            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { is_success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }

        SendResponse(response, jsonResponse, statusCode);
    }

    public void GetRobotsObs(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get Robot Observations");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";

        try
        {

            Dictionary<string, object> GetRobotInfoDict = ToDict(request);
            Debug.Log("GetRobotInfoDict: " + GetRobotInfoDict);

            if (GetRobotInfoDict == null || !GetRobotInfoDict.ContainsKey("robot_list"))
            {
                throw new ArgumentException("Missing or invalid 'robot_list' in the request.");
            }

            JArray jArray = GetRobotInfoDict["robot_list"] as JArray;
            if (jArray == null)
            {
                throw new ArgumentException("'robot_list' must be a valid JArray.");
            }

            List<string> robotNameList = jArray.ToObject<List<string>>();
            Debug.Log("robotNameList: " + robotNameList[0]);

            GameObject robot = GameObject.Find("getObj");
            if (robot == null)
            {
                throw new Exception("Robot object 'getObj' not found in the scene.");
            }

            EnvController envController = robot.GetComponent<EnvController>();
            if (envController == null)
            {
                throw new Exception("RobotController component not found on the 'getObj' GameObject.");
            }

            Dictionary<string, List<string>> responseJson = envController.GetRobotsObs(robotNameList);

            if (responseJson == null || responseJson.Count == 0)
            {
                Debug.LogWarning("responseJson is empty or null. Returning minimal response.");

                JObject jsonObject = new JObject
                {
                    { "is_success", true },
                    { "error_info", "Null" }
                };

                jsonResponse = JsonConvert.SerializeObject(jsonObject, Formatting.Indented);
            }
            else
            {

                jsonResponse = JsonConvert.SerializeObject(responseJson, Formatting.Indented);

                JObject jsonObject = JObject.Parse(jsonResponse);
                jsonObject.Add("is_success", true);
                jsonObject.Add("error_info", "Null");

                jsonResponse = JsonConvert.SerializeObject(jsonObject, Formatting.Indented);
            }

        }
        catch (Exception ex)
        {

            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { is_success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }

        SendResponse(response, jsonResponse, statusCode);
    }

    public void RobotPickApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Robot pick Obj");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            Dictionary<string, object> robotPickDict = ToDict(request);
            foreach (var entry in robotPickDict)
            {
                string robotName = entry.Key;
                Dictionary<string, object> robotData = ObjToDict(entry.Value);
                string ObjName = robotData["object_name"].ToString();

                GameObject robot = GameObject.Find(robotName);
                RobotController robotController = robot.GetComponent<RobotController>();
                if (robotController != null)
                {
                    robotController.Pick(ObjName, robotName);
                }
                else
                {
                    Debug.LogWarning($"Robot with name {robotName} not found.");
                }
            }
            jsonResponse = JsonConvert.SerializeObject(new { is_success = true, error_info = "Null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void RobotPlaceApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Robot pick Obj");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            Dictionary<string, object> robotPickDict = ToDict(request);
            foreach (var entry in robotPickDict)
            {
                string robotName = entry.Key;
                Dictionary<string, object> robotData = ObjToDict(entry.Value);
                string ObjName = robotData["object_name"].ToString();
                Vector3 targetPosition = ParseVector3(robotData["target_location"]);
                Vector3 targetRotation = ParseVector3(robotData["target_rotation"]);

                GameObject robot = GameObject.Find(robotName);
                RobotController robotController = robot.GetComponent<RobotController>();
                if (robotController != null)
                {
                    robotController.Place(ObjName, targetPosition, targetRotation);
                }
                else
                {
                    Debug.LogWarning($"Robot with name {robotName} not found.");
                }
            }
            jsonResponse = JsonConvert.SerializeObject(new { is_success = true, error_info = "Null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { is_success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }
    public void RobotPullApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Robot Pull Obj");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";
        string res = ""; 

        try
        {

            Dictionary<string, object> robotPickDict = ToDict(request);

            foreach (var entry in robotPickDict)
            {
                string robotName = entry.Key;
                Dictionary<string, object> robotData = ObjToDict(entry.Value);
                string ObjName = robotData["object_name"].ToString();
                string direction = robotData["direction"].ToString();

                GameObject robot = GameObject.Find(robotName);
                RobotController robotController = robot?.GetComponent<RobotController>(); 

                if (robotController != null)
                {
                    res = robotController.Pull(ObjName, robotName, direction); 
                }
                else
                {
                    Debug.LogWarning($"Robot with name {robotName} not found.");
                    res = $"Robot {robotName} not found"; 
                }
            }

            jsonResponse = JsonConvert.SerializeObject(new { result = res, is_success = true, error_info = "Null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }

        SendResponse(response, jsonResponse, statusCode);
    }

    public void RobotJointPullApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get Robot Observations");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";

        try
        {

            Dictionary<string, object> GetRobotInfoDict = ToDict(request);
            Debug.Log("GetRobotInfoDict: " + GetRobotInfoDict);

            if (GetRobotInfoDict == null || !GetRobotInfoDict.ContainsKey("robot_list"))
            {
                throw new ArgumentException("Missing or invalid 'robot_list' in the request.");
            }

            if (GetRobotInfoDict == null || !GetRobotInfoDict.ContainsKey("object_name"))
            {
                throw new ArgumentException("Missing or invalid 'object_name' in the request.");
            }

            if (GetRobotInfoDict == null || !GetRobotInfoDict.ContainsKey("direction"))
            {
                throw new ArgumentException("Missing or invalid 'direction' in the request.");
            }

            JArray jArray = GetRobotInfoDict["robot_list"] as JArray;
            if (jArray == null)
            {
                throw new ArgumentException("'robot_list' must be a valid JArray.");
            }
            string objectName = GetRobotInfoDict["object_name"].ToString();
            string direction = GetRobotInfoDict["direction"].ToString();

            List<string> robotNameList = jArray.ToObject<List<string>>();
            Debug.Log("robotNameList: " + robotNameList[0]);

            GameObject robot = GameObject.Find("getObj");
            if (robot == null)
            {
                throw new Exception("Robot object 'getObj' not found in the scene.");
            }

            EnvController envController = robot.GetComponent<EnvController>();
            if (envController == null)
            {
                throw new Exception("RobotController component not found on the 'getObj' GameObject.");
            }

            string res = envController.JointPull(robotNameList, objectName, direction);

            jsonResponse = JsonConvert.SerializeObject(new { result = res, is_success = true, error_info = "Null" });
        }
        catch (Exception ex)
        {

            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { is_success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }

        SendResponse(response, jsonResponse, statusCode);
    }

    public bool RobotsCommunicateApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Robots communicate");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";
        try
        {
            Dictionary<string, object> communicationData = ToDict(request);
            foreach (var entry in communicationData)
            {
                string robotName = entry.Key;
                Debug.Log("robotName:" + robotName);
                Dictionary<string, object> robotData = ObjToDict(entry.Value);
                string text = robotData["text"].ToString();
                Vector3 mark_position = ParseVector3(robotData["mark_position"]);
                Debug.Log("text:" + text);

                string img = "a";
                GameObject robot = GameObject.Find(robotName);
                if (robot == null) throw new Exception($"GameObject '{robotName}' not found.");
                RobotController robotController = robot.GetComponent<RobotController>();
                if (robotController == null) throw new Exception($"RobotController component not found on '{robotName}'.");
                Debug.Log("communicate1:");
                robotController.CommunicateWithHuman(robotName, text, img, mark_position);

            }
            jsonResponse = JsonConvert.SerializeObject(new { is_success = true, error_info = (string)null });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { is_success = false, error_info = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
        return true;

    }

    public void GetRobotsRgbdApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get robots rgbd");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        Dictionary<string, Dictionary<string, string>> responds = new Dictionary<string, Dictionary<string, string>>();
        try
        {

            Dictionary<string, object> robotsRgbd = ToDict(request);

            foreach (var entry in robotsRgbd)
            {
                Dictionary<string, string> singleRobotResponds = new Dictionary<string, string>();
                string robotName = entry.Key;
                Dictionary<string, string> imgAtt = new Dictionary<string, string>();
                Type type = entry.Value.GetType();
                Debug.Log("entry.Value" + entry.Value);
                string jsonString = JsonConvert.SerializeObject(entry.Value);
                JObject jsonObject = JObject.Parse(jsonString);
                string rgbOrRgbd = jsonObject["rgbOrRgbd"].ToString();
                string sizeString = jsonObject["size"].ToString();
                int[] sizeArray = JsonConvert.DeserializeObject<int[]>(sizeString);

                int width = sizeArray[0];
                int height = sizeArray[1];
                Debug.Log(height);
                GameObject robot = GameObject.Find(robotName);
                Debug.Log(robot);
                RobotController robotController = robot.GetComponent<RobotController>();
                Debug.Log(robotController);
                if (robotController != null)
                {
                    (string rgbBase64, string depthBase64) = robotController.GetRobotRgbdBase64(rgbOrRgbd, robotName, width, height);
                    singleRobotResponds.Add("rgb", rgbBase64);
                    singleRobotResponds.Add("depth", depthBase64);
                    responds.Add(robotName, singleRobotResponds);
                }
                else
                {
                    Debug.LogWarning($"Robot with name {robotName} not found.");
                }
            }
            jsonResponse = JsonConvert.SerializeObject(responds, Formatting.Indented);
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void GetCommunicationStatusApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get Communication status");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        Dictionary<string, object> responds = new Dictionary<string, object>();
        try
        {
            GameObject sceneSwitcherObject = GameObject.Find("getObj");
            EnvController envController = sceneSwitcherObject.GetComponent<EnvController>(); ;
            Dictionary<string, string>  CommunicationStatus = envController.GetCommunicationStatus();
            responds.Add("info",CommunicationStatus);
            responds.Add("success", "true");
            responds.Add("message", "null");
            jsonResponse = JsonConvert.SerializeObject(responds, Formatting.Indented);
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void ObjectsTeleportApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Objects teleport");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";

        try
        {

            Dictionary<string, object> objsTeleport = ToDict(request);

            HashSet<string> keysToKeep = new HashSet<string>(objsTeleport.Keys);

            GameObject pickUpableObjects = GameObject.Find("PickUpableObjects");
            if (pickUpableObjects != null)
            {

                foreach (Transform child in pickUpableObjects.transform)
                {
                    if (keysToKeep.Contains(child.gameObject.name))
                    {
                        if (!child.gameObject.activeSelf)
                        {
                            Debug.Log($"Activating child: {child.gameObject.name}");
                            child.gameObject.SetActive(true);
                        }
                    }
                    else
                    {
                        if (child.gameObject.activeSelf)
                        {
                            Debug.Log($"Deactivating child: {child.gameObject.name}");
                            child.gameObject.SetActive(false);
                        }
                    }
                }
            }
            else
            {
                Debug.LogWarning("PickUpableObjects GameObject not found.");
            }

            foreach (var entry in objsTeleport)
            {
                string objectName = entry.Key;
                Debug.Log(entry.Key);
                string jsonString = JsonConvert.SerializeObject(entry.Value);
                JObject jsonObject = JObject.Parse(jsonString);
                Vector3 targetPosition = ParseVector3(jsonObject["init_location"]);
                Vector3 targetRotation = ParseVector3(jsonObject["init_rotation"]);
                Debug.Log(targetPosition);
                Debug.Log(targetRotation);

                GameObject getObj = GameObject.Find("getObj");
                ObjectController objectController = getObj.GetComponent<ObjectController>();
                if (getObj != null)
                {
                    objectController.Teleport(targetPosition, targetRotation, objectName);
                }
                else
                {
                    Debug.LogWarning($"Robot with name {objectName} not found.");
                }
            }
            jsonResponse = JsonConvert.SerializeObject(new { is_success = true, error_info = "Null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }

        SendResponse(response, jsonResponse, statusCode);
    }

    public void ObjectsDeleteApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Objects Delete");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            Dictionary<string, object> objectDeleteDict = ToDict(request);
            JArray jArray = objectDeleteDict["object_list"] as JArray;
            List<string> objectList = jArray.ToObject<List<string>>();
            GameObject singleObject = GameObject.Find("getObj");
            ObjectController objectController = singleObject.GetComponent<ObjectController>();

            foreach (var entry in objectList)
            {

                objectController.Remove(objectList);
            }
            jsonResponse = JsonConvert.SerializeObject(new { is_success = true, error_info = "Null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void ObjectsAddApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Objects Add");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        try
        {

            Dictionary<string, object> objectsAddDict = ToDict(request);
            GameObject getObject = GameObject.Find("getObj");
            ObjectController objectController = getObject.GetComponent<ObjectController>();

            foreach (var entry in objectsAddDict)
            {
                string objectName = entry.Key;
                Debug.Log(entry.Value);
                Dictionary<string, object> singleObject = ObjToDict(entry.Value);
                string type = singleObject["type"].ToString();
                string name = singleObject["name"].ToString();
                Vector3 location = ParseVector3(singleObject["init_location"]);
                Vector3 rotation = ParseVector3(singleObject["init_rotation"]);
                objectController.ObjectAdd(type, name, location, rotation);
            }
            jsonResponse = JsonConvert.SerializeObject(new { is_success = true, error_info = "Null" });
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void GetReachablePointsApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Get Reachable Points");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        Dictionary<string, object> responds = new Dictionary<string, object>();
        try
        {

            Dictionary<string, object> objectsAddDict = ToDict(request);
            GameObject getObject = GameObject.Find("getObj");
            EnvController objectController = getObject.GetComponent<EnvController>();
            string step = objectsAddDict["step_size"].ToString();
            float stepSize = Convert.ToSingle(step);
            List<string> reachablePoints = objectController.GetReachablePoints(stepSize);
            responds.Add("reachable_point", reachablePoints);
            responds.Add("success", "true");
            responds.Add("message", "null");
            jsonResponse = JsonConvert.SerializeObject(responds, Formatting.Indented);
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    public void IsObjectInViewApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        Debug.Log("Is Object In View");
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "sever error";
        Dictionary<string, object> responds = new Dictionary<string, object>();
        try
        {

            Dictionary<string, object> objectsAddDict = ToDict(request);
            GameObject getObject = GameObject.Find("getObj");
            EnvController objectController = getObject.GetComponent<EnvController>();
            string robotName = objectsAddDict["robot_name"].ToString();
            string objectName = objectsAddDict["object_name"].ToString();
            bool isObjectInView = objectController.IsObjectInView(robotName, objectName);
            responds.Add("is_object_in_view", isObjectInView);
            responds.Add("success", "true");
            responds.Add("message", "null");
            jsonResponse = JsonConvert.SerializeObject(responds, Formatting.Indented);
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.InternalServerError;
        }
        SendResponse(response, jsonResponse, statusCode);
    }

    private void SendResponse(HttpListenerResponse response, string jsonResponse, HttpStatusCode statusCode)
    {
        byte[] buffer = System.Text.Encoding.UTF8.GetBytes(jsonResponse);
        response.ContentLength64 = buffer.Length;
        response.ContentType = "application/json";
        response.StatusCode = (int)statusCode;
        response.StatusDescription = statusCode.ToString();

        using (Stream output = response.OutputStream)
        {
            output.Write(buffer, 0, buffer.Length);
        }
    }
    static Dictionary<string, object> ToDict(HttpListenerRequest request)
    {

        if (request.ContentType != "application/json")
        {
            throw new NotSupportedException("Only JSON payload is supported.");
        }

        using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
        {
            string requestBody = reader.ReadToEnd();
            return JsonConvert.DeserializeObject<Dictionary<string, object>>(requestBody);
        }
    }
    static Dictionary<string, object> ToDictWithValueS(HttpListenerRequest request)
    {

        if (request.ContentType != "application/json")
        {
            throw new NotSupportedException("Only JSON payload is supported.");
        }

        using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
        {
            string requestBody = reader.ReadToEnd();
            return JsonConvert.DeserializeObject<Dictionary<string, object>>(requestBody);
        }
    }
    static Dictionary<string, object> ObjToDict(object obj)
    {
        string json = JsonConvert.SerializeObject(obj);
        return JsonConvert.DeserializeObject<Dictionary<string, object>>(json);
    }
    static List<object> ExtractValuesToList(Dictionary<string, object> dictionary, List<string> keys)
    {
        var valuesList = new List<object>();

        foreach (var key in keys)
        {
            if (dictionary.TryGetValue(key, out object value))
            {
                valuesList.Add(value);
            }
            else
            {
                Console.WriteLine($"Key '{key}' not found in the dictionary.");
            }
        }

        return valuesList;
    }
    private Vector3 ParseVector3(object obj)
    {
        if (obj is JArray array && array.Count == 3)
        {
            float x = array[0].ToObject<float>();
            float y = array[1].ToObject<float>();
            float z = array[2].ToObject<float>();
            return new Vector3(x, y, z);
        }
        else
        {
            Debug.LogError("Invalid vector format.");
            return Vector3.zero;
        }
    }
    private Vector2 ParseVector2(object obj)
    {
        if (obj is JArray array && array.Count == 2)
        {
            float x = array[0].ToObject<float>();
            float y = array[1].ToObject<float>();
            return new Vector2(x, y);
        }
        else
        {
            Debug.LogError("Invalid vector format.");
            return Vector2.zero;
        }
    }
}
