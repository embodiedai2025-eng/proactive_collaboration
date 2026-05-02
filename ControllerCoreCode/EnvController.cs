using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Linq;
using UnityEngine.AI;
using UnityEngine.UI;
using System;


public class EnvController : MonoBehaviour
{
    private bool isPaused = false;
    public string npcNameContains = "Robot"; 
    public Color[] pathColors = new Color[]
    {
        Color.red,
        Color.blue,
        Color.green,
        Color.yellow,
        Color.magenta,
        Color.cyan,
        Color.white,
        Color.gray
    }; 
    public LineRenderer[] lineRenderers;
    public GameObject[] npcs;
    public Vector3[][] previousPositions;
    public float boundarySize = 100f;

    public int targetDisplay = 1;

    public Dictionary<string, List<string>> GetRobotsObs(List<string> robotNameList) 
    {
        Debug.Log("Starting GetRobotsObs method...");

        GameObject getObj = GameObject.Find("getObj");
        if (getObj == null)
        {
            Debug.LogError("Robot object 'getObj' not found in the scene.");
            throw new Exception("Robot object 'getObj' not found in the scene.");
        }

        Debug.Log("'getObj' successfully found in the scene.");

        Dictionary<string, List<string>> result = new Dictionary<string, List<string>>();

        foreach (string robotName in robotNameList)
        {
            Debug.Log($"Processing robot: {robotName}");

            GameObject robot = GameObject.Find(robotName);
            if (robot == null)
            {
                Debug.LogError($"Robot object '{robotName}' not found in the scene.");
                throw new Exception($"Robot object '{robotName}' not found in the scene.");
            }

            Transform displayCameraTransform = robot.transform.Find("displayCamera");
            if (displayCameraTransform == null)
            {
                Debug.LogError($"'displayCamera' not found in robot '{robotName}'.");
                throw new Exception($"'displayCamera' not found in robot '{robotName}'.");
            }

            Debug.Log($"'displayCamera' found for robot '{robotName}'.");

            Camera displayCamera = displayCameraTransform.GetComponent<Camera>();
            if (displayCamera == null)
            {
                Debug.LogError($"Camera component not found on 'displayCamera' of robot '{robotName}'.");
                throw new Exception($"Camera component not found on 'displayCamera' of robot '{robotName}'.");
            }

            Debug.Log($"Camera component found on 'displayCamera' for robot '{robotName}'.");

            CameraController cameraController = getObj.GetComponent<CameraController>();
            if (cameraController == null)
            {
                Debug.LogError("CameraController component not found on 'getObj'.");
                throw new Exception("CameraController component not found on 'getObj'.");
            }

            Debug.Log("CameraController component found on 'getObj'.");

            List<string> obsList;
            try
            {
                obsList = cameraController.getObjectsInView(displayCamera);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error while getting objects in view for robot '{robotName}': {ex.Message}");
                throw;
            }

            Debug.Log($"Objects in view for robot '{robotName}': {string.Join(", ", obsList)}");

            result.Add(robotName, obsList);
        }

        Debug.Log("GetRobotsObs method completed successfully.");
        return result;
    }

    public string JointPull(List<string> robotNames,string ObjName,string direction)
    {
        
        GameObject obj = GameObject.Find(ObjName);

        
        string pullPointsName = ObjName + "_PullPoints";
        GameObject pullPoints = GameObject.Find(pullPointsName);

        
        if (obj == null || pullPoints == null)
        {
            return "Object or pull points not found!";
        }

        
        Transform pullPointsTransform = pullPoints.transform;

        
        if (pullPointsTransform == null)
        {
            return "Pull points transform not found!";
        }

        
        Vector3 pulledPosition = obj.transform.position;
        Vector3 pulledDistance = Vector3.zero; 

        
        foreach (Transform child in pullPointsTransform)
        {
            double pullPointX = Math.Round(child.position.x, 2);
            double pullPointY = Math.Round(child.position.y, 2);
            double pullPointZ = Math.Round(child.position.z, 2);
            double objPosX = Math.Round(obj.transform.position.x, 2);
            double objPosY = Math.Round(obj.transform.position.y, 2);
            double objPosZ = Math.Round(obj.transform.position.z, 2);
            
            if (direction == "(0,0,1)" && pullPointX == objPosX &&
                pullPointY == objPosY && pullPointZ > objPosZ)
            {
                pulledPosition = child.position;
                pulledDistance = new Vector3(0, 0, child.position.z - obj.transform.position.z);
                break;
            }
            else if (direction == "(0,0,-1)" && pullPointX == objPosX &&
                     pullPointY == objPosY && pullPointZ < objPosZ)
            {
                pulledPosition = child.position;
                pulledDistance = new Vector3(0, 0, child.position.z - obj.transform.position.z);
                break;
            }
            else if (direction == "(1,0,0)" && pullPointX > objPosX &&
                     pullPointY == objPosY && pullPointZ == objPosZ)
            {
                pulledPosition = child.position;
                pulledDistance = new Vector3(child.position.x - obj.transform.position.x, 0, 0);
                break;
            }
            else if (direction == "(-1,0,0)" && pullPointX < objPosX &&
                     pullPointY == objPosY && pullPointZ == objPosZ)
            {
                pulledPosition = child.position;
                pulledDistance = new Vector3(child.position.x - obj.transform.position.x, 0, 0);
                break;
            }
            Debug.Log("NOT GOOD !!!!PULL!!!!!POINTS");
            Debug.Log("pullpoint position");
            Debug.Log(pullPointX);
            Debug.Log(pullPointY);
            Debug.Log(pullPointZ);
            Debug.Log("obj position");
            Debug.Log(objPosX);
            Debug.Log(objPosY);
            Debug.Log(objPosZ);
            Debug.Log("relations");
            Debug.Log(pullPointZ > objPosZ);
            Debug.Log(direction == "(0,0,1)");
            Debug.Log(pullPointY == objPosY);
            Debug.Log(pullPointX == objPosX);
        }

        
        if (obj.transform.position != pulledPosition)
        {
            obj.transform.position = pulledPosition;
            
            foreach (string robotName in robotNames)
            {
                GameObject robot = GameObject.Find(robotName);
                if (robot != null)
                {
                    robot.transform.position += pulledDistance;
                }
            }
            return "Success";
        }

        
        return "Wrong Direction";
    }

    public void SelectScene(int SenceIndex)
    {
        SceneManager.LoadScene(SenceIndex);
    }

    public void SingleRobotSetup(string type, string name, Vector3 position, Vector3 rotation, string armLength, string strength, string robotLow, string robotHigh)
    {
        
        
        
        GameObject existingRobot = GameObject.Find(name);
        if (existingRobot != null)
        {
            Debug.Log($"Robot with name '{name}' already exists. Skipping initialization.");
            return; 
        }
        string relativePrefabLoc = "Robots/" + type;
        GameObject prefabToInstantiate = Resources.Load<GameObject>(relativePrefabLoc); 
        GameObject newRobotObj = Instantiate(prefabToInstantiate, position, Quaternion.Euler(rotation)); 
        newRobotObj.name = name; 
        RobotController singleRobotController = newRobotObj.GetComponent<RobotController>();
        singleRobotController.robotType = type;
        singleRobotController.armLength = armLength;
        singleRobotController.strength = strength;
        singleRobotController.robotLow = robotLow;
        singleRobotController.robotHigh = robotHigh;
    }

    public void SceneReset()
    {
        Scene currentScene = SceneManager.GetActiveScene();
        SceneManager.LoadScene(currentScene.name);
    }
    
    public void GamePasue()
    {
        Time.timeScale = 0;
        isPaused = true;
        Debug.Log("isPaused"+isPaused);
        GameObject hum = GameObject.Find("Hum");
        GameObject CommunicationUI = hum.transform.Find("CommunicationUI").gameObject;
        GameObject gamePauseObject = CommunicationUI.transform.Find("game_pause_panel").gameObject;
        gamePauseObject.SetActive(true);
    }
    
    public void GameResume()
    {
        if (Time.timeScale == 0)
        {
            Time.timeScale = 1;
            isPaused = false;
            GameObject hum = GameObject.Find("Hum");
            GameObject CommunicationUI = hum.transform.Find("CommunicationUI").gameObject;
            GameObject gamePauseObject = CommunicationUI.transform.Find("game_pause_panel").gameObject;
            gamePauseObject.SetActive(false);
        }
        
    }

    public Dictionary<string, string> GetCommunicationStatus()
    {
        npcs = GameObject.FindObjectsOfType<GameObject>();
        npcs = System.Array.FindAll(npcs, npc => npc.name.Contains(npcNameContains));
        Dictionary<string, string> CommunicationStatus = new Dictionary<string, string>();
        
        foreach (GameObject obj in npcs)
        {
            Debug.Log("comfirmState"+obj.GetComponent<RobotController>().comfirmInfo.Count);
            if (obj.GetComponent<RobotController>().comfirmInfo.Count == 0)
            {
                CommunicationStatus.Add(obj.name, "null");
            }
            else 
            {
                string comfirmState = obj.GetComponent<RobotController>().comfirmInfo[obj.GetComponent<RobotController>().comfirmInfo.Count - 1];
                CommunicationStatus.Add(obj.name, comfirmState);
            }
           
        }
        return CommunicationStatus;
    }

    public List<string> GetReachablePoints(float step)
    {
        Bounds bounds = new Bounds(Vector3.zero, Vector3.one * boundarySize);
        List<string> reachablePoints = new List<string>();
        for (float x = -10; x <= 10; x += step)
        {
            for (float z = bounds.min.z; z <= bounds.max.z; z += step)
            {
                Vector3 point = new Vector3(x, 0f, z);
                
                if (NavMesh.SamplePosition(point, out NavMeshHit hit, 0.1f, NavMesh.AllAreas))
                {
                    string vecString = "("+$"{hit.position.x:F1},{hit.position.y:F1},{hit.position.z:F1}"+")"; 
                    reachablePoints.Add(vecString);
                }
            }
        }
        return reachablePoints;
    }

    public bool IsObjectInView(string robotName,string objName)
    {
        GameObject robot = GameObject.Find(robotName);
        Transform displayCameraTransform = robot.transform.Find("displayCamera");
        Camera displayCamera = displayCameraTransform.GetComponent<Camera>();
        GameObject obj = GameObject.Find(objName);
        Renderer objRenderer = obj.GetComponent<Renderer>();
        if (objRenderer == null)
        {
            Debug.LogError($"{obj.name} does not have a Renderer component.");
            return false;
        }

        
        Plane[] planes = GeometryUtility.CalculateFrustumPlanes(displayCamera);
        if (GeometryUtility.TestPlanesAABB(planes, objRenderer.bounds))
        {
            Debug.Log("TestPlanesAABB true");
            
            

            Bounds bounds = objRenderer.bounds;
            Vector3[] pointsToCheck = new Vector3[]
            {
                bounds.center,
                bounds.min,
                bounds.max,
                new Vector3(bounds.min.x, bounds.min.y, bounds.max.z),
                new Vector3(bounds.min.x, bounds.max.y, bounds.min.z),
                new Vector3(bounds.max.x, bounds.min.y, bounds.min.z),
                new Vector3(bounds.max.x, bounds.max.y, bounds.min.z),
                new Vector3(bounds.max.x, bounds.min.y, bounds.max.z),
                new Vector3(bounds.min.x, bounds.max.y, bounds.max.z)
            };

            foreach (var point in pointsToCheck)
            {
                if (IsPointVisible(displayCamera, point, obj))
                {
                    return true;
                }
            }
        }

        return false;
    }

    bool IsPointVisible(Camera cam, Vector3 point, GameObject obj)
    {
        RaycastHit hit;

        if (Physics.Linecast(cam.transform.position, point, out hit))
        {
            Debug.Log("hit.transform.name:"+hit.transform.name);
            Debug.Log("obj.name:" + obj.name);
            if (hit.transform.name == obj.name)
            {
                Debug.Log(obj.name + " occluded by " + hit.transform.name);
                return true;
            }
        }
        return false;
    }
}
