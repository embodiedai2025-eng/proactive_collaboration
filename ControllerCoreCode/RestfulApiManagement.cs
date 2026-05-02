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

            if (ScenceDict == null || !ScenceDict.ContainsKey("scene_id"))
            {
                throw new ArgumentException("Missing required field 'scene_id'.");
            }

            int SenceIndex = Convert.ToInt32(ScenceDict["scene_id"]);
            Debug.Log(SenceIndex);
            GameObject sceneSwitcherObject = GameObject.Find("getObj");
            EnvController envController = sceneSwitcherObject.GetComponent<EnvController>(); ;
            envController.SelectScene(SenceIndex);
            jsonResponse = JsonConvert.SerializeObject(new { success = true, message = "null" });
        }
        catch (ArgumentException ex)
        {
            Debug.LogError($"Invalid request: {ex.Message}");
            jsonResponse = JsonConvert.SerializeObject(new { success = false, message = ex.Message });
            statusCode = HttpStatusCode.BadRequest;
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
            
            Dictionary<string, Dictionary<string, object>> responseJson = objectController.GetObjInfo(objectList);
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

            bool includeObservationImage = false;
            if (GetRobotInfoDict.TryGetValue("include_observation_image", out object includeImgObj) && includeImgObj != null)
            {
                if (includeImgObj is bool b)
                {
                    includeObservationImage = b;
                }
                else
                {
                    bool.TryParse(includeImgObj.ToString(), out includeObservationImage);
                }
            }

            int imageWidth = 0;
            int imageHeight = 0;
            bool hasImageWidth = GetRobotInfoDict.TryGetValue("image_width", out object wObj) && wObj != null
                && int.TryParse(wObj.ToString(), out imageWidth) && imageWidth > 0;
            bool hasImageHeight = GetRobotInfoDict.TryGetValue("image_height", out object hObj) && hObj != null
                && int.TryParse(hObj.ToString(), out imageHeight) && imageHeight > 0;
            bool explicitImageSize = hasImageWidth && hasImageHeight;

            int imageMaxEdge = 1920;
            if (GetRobotInfoDict.TryGetValue("image_max_edge", out object maxEdgeObj) && maxEdgeObj != null
                && int.TryParse(maxEdgeObj.ToString(), out int me) && me > 0)
            {
                imageMaxEdge = Mathf.Clamp(me, 64, 8192);
            }

            bool includeDepth = false;
            if (GetRobotInfoDict.TryGetValue("include_depth", out object depthObj) && depthObj != null)
            {
                if (depthObj is bool bd)
                {
                    includeDepth = bd;
                }
                else
                {
                    bool.TryParse(depthObj.ToString(), out includeDepth);
                }
            }

            
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
                if (includeObservationImage)
                {
                    CameraController cameraController = robot.GetComponent<CameraController>();
                    if (cameraController == null)
                    {
                        jsonObject["observation_images"] = new JObject
                        {
                            { "error", "CameraController not found on getObj." }
                        };
                    }
                    else
                    {
                        JObject imagesObject = new JObject();
                        foreach (string robotName in robotNameList)
                        {
                            JObject oneRobotImage = new JObject();
                            GameObject robotGo = GameObject.Find(robotName);
                            if (robotGo == null)
                            {
                                oneRobotImage["error"] = $"Robot '{robotName}' not found.";
                                imagesObject[robotName] = oneRobotImage;
                                continue;
                            }
                            Transform displayCamTransform = robotGo.transform.Find("displayCamera");
                            if (displayCamTransform == null)
                            {
                                oneRobotImage["error"] = "'displayCamera' not found on robot.";
                                imagesObject[robotName] = oneRobotImage;
                                continue;
                            }
                            Camera displayCamera = displayCamTransform.GetComponent<Camera>();
                            if (displayCamera == null)
                            {
                                oneRobotImage["error"] = "Camera missing on displayCamera.";
                                imagesObject[robotName] = oneRobotImage;
                                continue;
                            }

                            int capW, capH;
                            ComputeImageCaptureSize(
                                displayCamera,
                                explicitImageSize ? imageWidth : 0,
                                explicitImageSize ? imageHeight : 0,
                                imageMaxEdge,
                                out capW,
                                out capH);
                            oneRobotImage["width"] = capW;
                            oneRobotImage["height"] = capH;

                            if (includeDepth)
                            {
                                (string rgbB64, string depthB64) = cameraController.CaptureRgbdPngBase64(displayCamera, capW, capH);
                                if (string.IsNullOrEmpty(rgbB64))
                                {
                                    oneRobotImage["error"] = "Failed to capture RGB.";
                                }
                                else
                                {
                                    oneRobotImage["rgb_base64"] = rgbB64;
                                }
                                if (string.IsNullOrEmpty(depthB64))
                                {
                                    oneRobotImage["depth_error"] = "Failed to capture depth.";
                                }
                                else
                                {
                                    oneRobotImage["depth_base64"] = depthB64;
                                }
                            }
                            else
                            {
                                string b64 = cameraController.CaptureRgbPngBase64(displayCamera, capW, capH);
                                if (string.IsNullOrEmpty(b64))
                                {
                                    oneRobotImage["error"] = "Failed to capture RGB.";
                                }
                                else
                                {
                                    oneRobotImage["rgb_base64"] = b64;
                                }
                            }
                            imagesObject[robotName] = oneRobotImage;
                        }
                        jsonObject["observation_images"] = imagesObject;
                    }
                }
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

    /// <summary>
    /// Returns a high-resolution RGB PNG (base64) from the scene top-down camera on a given Unity target display.
    /// target_display is 0-based (Unity Inspector "Display 1" = 0). Camera is resolved by name containing "TopDown".
    /// Optional JSON: target_display, image_max_edge, image_width + image_height (both required to force size).
    /// </summary>
    public void GetTopdownDisplayImageApi(HttpListenerRequest request, HttpListenerResponse response)
    {
        HttpStatusCode statusCode = HttpStatusCode.OK;
        string jsonResponse = "server error";

        try
        {
            Dictionary<string, object> dict = ParseJsonBodyToDictAllowEmpty(request);

            int targetDisplay = 0;
            if (dict.TryGetValue("target_display", out object tdObj) && tdObj != null
                && int.TryParse(tdObj.ToString(), out int tdParsed))
            {
                targetDisplay = Mathf.Clamp(tdParsed, 0, 7);
            }

            int imageMaxEdge = 1920;
            if (dict.TryGetValue("image_max_edge", out object meObj) && meObj != null
                && int.TryParse(meObj.ToString(), out int me) && me > 0)
            {
                imageMaxEdge = Mathf.Clamp(me, 64, 8192);
            }

            int imageWidth = 0;
            int imageHeight = 0;
            bool hasW = dict.TryGetValue("image_width", out object wObj) && wObj != null
                && int.TryParse(wObj.ToString(), out imageWidth) && imageWidth > 0;
            bool hasH = dict.TryGetValue("image_height", out object hObj) && hObj != null
                && int.TryParse(hObj.ToString(), out imageHeight) && imageHeight > 0;
            bool explicitImageSize = hasW && hasH;

            Camera topCam = FindTopdownCameraForDisplay(targetDisplay);
            if (topCam == null)
            {
                throw new Exception(
                    "No active enabled Camera with 'TopDown' in its name for target_display="
                    + targetDisplay
                    + " (Unity Inspector label: Display "
                    + (targetDisplay + 1)
                    + "). Assign your top-down camera to that display or pass a different target_display.");
            }

            GameObject getObj = GameObject.Find("getObj");
            if (getObj == null)
            {
                throw new Exception("GameObject 'getObj' not found; cannot capture.");
            }

            CameraController cameraController = getObj.GetComponent<CameraController>();
            if (cameraController == null)
            {
                throw new Exception("CameraController not found on 'getObj'.");
            }

            int capW, capH;
            ComputeImageCaptureSize(
                topCam,
                explicitImageSize ? imageWidth : 0,
                explicitImageSize ? imageHeight : 0,
                imageMaxEdge,
                out capW,
                out capH);
            string b64 = cameraController.CaptureRgbPngBase64(topCam, capW, capH);
            if (string.IsNullOrEmpty(b64))
            {
                throw new Exception("Failed to capture top-down RGB PNG.");
            }

            JObject jsonObject = new JObject
            {
                { "is_success", true },
                { "error_info", "Null" },
                { "target_display", targetDisplay },
                { "camera_name", topCam.gameObject.name },
                { "width", capW },
                { "height", capH },
                { "rgb_base64", b64 }
            };
            jsonResponse = jsonObject.ToString(Formatting.Indented);
        }
        catch (Exception ex)
        {
            Debug.LogError($"GetTopdownDisplayImageApi: {ex.Message}");
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

    static Dictionary<string, object> ParseJsonBodyToDictAllowEmpty(HttpListenerRequest request)
    {
        if (request.ContentType == null || request.ContentType.IndexOf("application/json", StringComparison.OrdinalIgnoreCase) < 0)
        {
            return new Dictionary<string, object>();
        }

        using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
        {
            string body = reader.ReadToEnd();
            if (string.IsNullOrWhiteSpace(body))
            {
                return new Dictionary<string, object>();
            }

            Dictionary<string, object> d = JsonConvert.DeserializeObject<Dictionary<string, object>>(body);
            return d ?? new Dictionary<string, object>();
        }
    }

    static Camera FindTopdownCameraForDisplay(int targetDisplay)
    {
        Camera fallback = null;
        foreach (Camera cam in UnityEngine.Object.FindObjectsOfType<Camera>(true))
        {
            if (cam == null || !cam.gameObject.activeInHierarchy || !cam.enabled)
            {
                continue;
            }

            if (cam.targetDisplay != targetDisplay)
            {
                continue;
            }

            string n = cam.gameObject.name;
            if (n.IndexOf("TopDown", StringComparison.OrdinalIgnoreCase) < 0)
            {
                continue;
            }

            if (string.Equals(n, "TopDownCamera", StringComparison.OrdinalIgnoreCase))
            {
                return cam;
            }

            if (fallback == null)
            {
                fallback = cam;
            }
        }

        return fallback;
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

    /// <summary>
    /// Chooses capture resolution. When reqW and reqH are both positive, uses that size (then scales down if needed).
    /// Otherwise uses the camera's pixel size so the render target aspect matches the live camera — preserving vertical FOV
    /// and horizontal extent vs a square/low-aspect forced size.
    /// </summary>
    static void ComputeImageCaptureSize(Camera cam, int reqW, int reqH, int maxEdge, out int outW, out int outH)
    {
        int w;
        int h;
        if (reqW > 0 && reqH > 0)
        {
            w = reqW;
            h = reqH;
        }
        else
        {
            int pw = cam != null ? cam.pixelWidth : 0;
            int ph = cam != null ? cam.pixelHeight : 0;
            if (pw < 2 || ph < 2)
            {
                float aspect = (cam != null && cam.aspect > 0.01f) ? cam.aspect : (16f / 9f);
                h = 720;
                w = Mathf.Max(1, Mathf.RoundToInt(h * aspect));
            }
            else
            {
                w = Mathf.Max(1, pw);
                h = Mathf.Max(1, ph);
            }
        }

        maxEdge = Mathf.Max(64, maxEdge);
        int maxDim = Mathf.Max(w, h);
        if (maxDim > maxEdge)
        {
            float scale = (float)maxEdge / maxDim;
            w = Mathf.Max(1, Mathf.RoundToInt(w * scale));
            h = Mathf.Max(1, Mathf.RoundToInt(h * scale));
        }

        outW = w;
        outH = h;
    }
}
