using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ObjectController : MonoBehaviour
{

    public string ObjectName;

    public void Teleport(Vector3 targetPosition, Vector3 targetRotation, string objectName)
    {
        GameObject obj = GameObject.Find(objectName);
        obj.transform.position = targetPosition;
        obj.transform.rotation = Quaternion.Euler(targetRotation);
    }

    public Dictionary<string, Dictionary<string, string>> GetRobotStatus(List<string> inputList)
    {
        Dictionary<string, Dictionary<string, string>> result = new Dictionary<string, Dictionary<string, string>>();
        try
        {
            int robotCount = 0;

            foreach (string robotName in inputList)
            {

                GameObject obj = GameObject.Find(robotName);
                if (obj != null)
                {

                    Dictionary<string, string> currentStatus = OneRobotStatus(obj);
                    result.Add(robotName, currentStatus);
                }
                else
                {
                    Debug.LogWarning("Robot " + robotName + " not found in the scene.");
                }
                robotCount++;
            }

        }
        catch (System.Exception e)
        {

            Debug.LogError("Error collecting object data: " + e.ToString());
        }
        return result;
    }

    public Dictionary<string, string> OneRobotStatus(GameObject robot)
    {
        Dictionary<string, string> result = new Dictionary<string, string>();
        GameObject hand = robot.transform.Find("Hand")?.gameObject;
        if (hand != null)
        {
            result.Add("hand", "True");

            Vector3 handPosition = hand.transform.position;

            string handPositionString = $"({handPosition.x}, {handPosition.y}, {handPosition.z})";
            result.Add("handPosition", handPositionString);

            int childCount = hand.transform.childCount;
            if (childCount > 0)
            {
                result.Add("isHold", "True");
                string holding = "";
                foreach (Transform child in hand.transform)
                {
                    holding += child.name;
                }
                result.Add("Holding", holding);
            }
            else
            {
                result.Add("isHold", "False");
            }
        }
        else
        {
            result.Add("hand", "False");
        }
        RobotController singleRobotController = robot.GetComponent<RobotController>();
        result.Add("robotType", singleRobotController.robotType);
        result.Add("armLength", singleRobotController.armLength);
        result.Add("strength", singleRobotController.strength);
        result.Add("robotLow", singleRobotController.robotLow);
        result.Add("robotHigh", singleRobotController.robotHigh);

        return result;
    }

    public Dictionary<string, string> GetObjectType(List<string> inputList)
    {
        Dictionary<string, string> result = new Dictionary<string, string>();
        try
        {
            int objCount = 0;

            foreach (string objectName in inputList)
            {

                GameObject obj = GameObject.Find(objectName);
                Transform parentTransform = obj.transform.parent;
                if (parentTransform != null)
                {

                    string objectType = parentTransform.gameObject.name;
                    result.Add(objectName, objectType);
                }
                else
                {
                    result.Add(objectName, "None");
                }
                Transform putPoints = obj.transform.Find("putPoints");
                if (putPoints != null)
                {
                    result.Add(objectName + "Placeable", "True");
                    string putPointsLocs = "";
                    foreach (Transform child in putPoints)
                    {

                        putPointsLocs += child.position.ToString() + " ; ";
                        Debug.Log("Child: " + child.name + " Position: " + child.position);
                    }
                    result.Add(objectName + "PutPoints", putPointsLocs);
                } 
                else
                {
                    result.Add(objectName + "Placeable", "False");
                }
                result.Add(objectName + "EdgePoints", GetEdgePoints(obj));
                objCount++;
            }
        }
        catch (System.Exception e)
        {

            Debug.LogError("Error collecting object data: " + e.ToString());
        }
        return result;
    }

    string GetEdgePoints(GameObject obj)
    {
        string res = "";
        Renderer[] objRenderers = obj.GetComponentsInChildren<Renderer>();
        foreach (Renderer objRenderer in objRenderers)
        {
            Bounds bounds = objRenderer.bounds;
            Vector3[] pointsToCheck = new Vector3[]
                {
                    bounds.center,
                    GetTwoThirdsPoint(bounds.center, new Vector3(bounds.min.x, bounds.min.y, bounds.min.z)),  
                    GetTwoThirdsPoint(bounds.center, new Vector3(bounds.min.x, bounds.min.y, bounds.max.z)), 
                    GetTwoThirdsPoint(bounds.center, new Vector3(bounds.min.x, bounds.max.y, bounds.min.z)),  
                    GetTwoThirdsPoint(bounds.center, new Vector3(bounds.min.x, bounds.max.y, bounds.max.z)),  
                    GetTwoThirdsPoint(bounds.center, new Vector3(bounds.max.x, bounds.min.y, bounds.min.z)),  
                    GetTwoThirdsPoint(bounds.center, new Vector3(bounds.max.x, bounds.min.y, bounds.max.z)),  
                    GetTwoThirdsPoint(bounds.center, new Vector3(bounds.max.x, bounds.max.y, bounds.min.z)),  
                    GetTwoThirdsPoint(bounds.center, new Vector3(bounds.max.x, bounds.max.y, bounds.max.z)),  
                };
            foreach(Vector3 points in pointsToCheck)
            {
                res += points.ToString() + " ; ";
            }            
        }
        return res;
    }

    public Vector3 GetTwoThirdsPoint(Vector3 start, Vector3 end)
    {
        return start + (2f / 3f) * (end - start);
    }
    public Dictionary<string, Dictionary<string, List<float>>> GetObjInfo(List<string> inputList)
    {
        Dictionary<string, Dictionary<string, List<float>>> result = new Dictionary<string, Dictionary<string, List<float>>>();

        try
        {

            if (inputList.Count > 0 && inputList[0] == "all")
            {

                GameObject[] allObjects = GameObject.FindObjectsOfType<GameObject>();
                int objectCount = 0;

                foreach (GameObject obj in allObjects)
                {
                    Debug.Log("objectCount:" + objectCount);
                    string objectName = "object " + objectCount + " name"; 
                    objectCount++;

                    Vector3 position = obj.transform.position;
                    Quaternion rotation = obj.transform.rotation;

                    List<float> positionList = new List<float> { position.x, position.y, position.z };
                    List<float> rotationList = new List<float> { rotation.eulerAngles.x, rotation.eulerAngles.y, rotation.eulerAngles.z };

                    result.Add(objectName, new Dictionary<string, List<float>>
                    {
                        { "location", positionList },
                        { "rotation", rotationList }
                    });
                }
            }
            else 
            {
                int objectCount = 0;

                foreach (string objectName in inputList)
                {

                    GameObject obj = GameObject.Find(objectName);
                    if (obj != null)
                    {

                        Vector3 position = obj.transform.position;
                        Quaternion rotation = obj.transform.rotation;

                        List<float> positionList = new List<float> { position.x, position.y, position.z };
                        List<float> rotationList = new List<float> { rotation.eulerAngles.x, rotation.eulerAngles.y, rotation.eulerAngles.z };

                        Dictionary<string, List<float>> status = new Dictionary<string, List<float>>
                        {
                            { "location", positionList },
                            { "rotation", rotationList }
                        };
                        result.Add(objectName, status);
                    }
                    else
                    {
                        Debug.LogWarning("Object '" + objectName + "' not found in the scene.");
                    }

                    objectCount++;
                }
            }
        }
        catch (System.Exception e)
        {

            Debug.LogError("Error collecting object data: " + e.ToString());
        }

        return result;
    }
    public Dictionary<string, Dictionary<string, string>> GetObjNeighbors(List<string> inputList)
    {
        Dictionary<string, Dictionary<string, string>> result = new Dictionary<string, Dictionary<string, string>>();

        try
        {
            int objectCount = 0;

            foreach (string objectName in inputList)
            {

                GameObject obj = GameObject.Find(objectName);
                if (obj != null)
                {

                    Dictionary<string, string> neighbors = FindNeighborsWithRaycast(obj);
                    result.Add(objectName, neighbors);
                }
                else
                {
                    Debug.LogWarning("Object '" + objectName + "' not found in the scene.");
                }

                objectCount++;
            }

        }
        catch (System.Exception e)
        {

            Debug.LogError("Error collecting object data: " + e.ToString());
        }

        return result;
    }
    public float maxDistance = 1f;

    Dictionary<string, string> FindNeighborsWithRaycast(GameObject targetObject)
    {
        Dictionary<string, string> neighbors = new Dictionary<string, string>();

        Transform meshTransform = targetObject.transform.Find("mesh");
        if (meshTransform == null)
        {
            Debug.LogWarning($"The target object {targetObject.name} does not have a child named 'mesh'.");
            return neighbors;
        }

        Collider meshCollider = meshTransform.GetComponent<Collider>();
        if (meshCollider == null)
        {
            Debug.LogWarning($"The 'mesh' child of {targetObject.name} does not have a Collider component.");
            return neighbors;
        }

        Vector3 position = meshCollider.bounds.center;
        Vector3[] directions = { Vector3.forward, Vector3.back, Vector3.left, Vector3.right, Vector3.up, Vector3.down };

        foreach (Vector3 direction in directions)
        {

            RaycastHit[] hits = Physics.RaycastAll(position, direction, maxDistance);

            Debug.DrawRay(position, direction * maxDistance, Color.red, 5f);

            System.Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));

            foreach (RaycastHit hit in hits)
            {

                GameObject hitObject = hit.collider.gameObject;
                Debug.Log($"{targetObject.name} hit in direction {direction}: {hitObject.name}");

                if (hitObject == targetObject)
                {
                    continue;
                }

                string hitName = hitObject.name;

                if (hitName == "mesh")
                {

                    GameObject parentObject = hitObject.transform.parent?.gameObject;

                    Debug.Log($"{targetObject.name} hit in direction {direction}: {parentObject.name}");
                    if (parentObject != null && parentObject.name != targetObject.name)
                    {

                        neighbors[direction.ToString()] = parentObject.name;
                        Debug.Log($"{targetObject.name} Neighbor found in direction {direction}: {parentObject.name}");
                        break; 
                    }
                }
                else if (hitName != targetObject.name)
                {

                    neighbors[direction.ToString()] = hitName;
                    Debug.Log($"{targetObject.name} Neighbor found in direction {direction}: {hitName}");
                    break; 
                }
            }
        }

        return neighbors;
    }

    public void Remove(List<string> objectList)
    {
        foreach (string SingleObject in objectList)
        {
            GameObject obj = GameObject.Find(SingleObject);

            if (obj != null && obj.activeSelf)
            {
                obj.SetActive(false);
                Debug.Log("Object is now inactive.");
            }
            else if (obj != null)
            {
                Debug.Log("Object is already inactive.");
            }
            else
            {
                Debug.Log("Object not found.");
            }
        }
    }

    public void ObjectAdd(string prefabName, string newObjectName, Vector3 position, Vector3 rotation)
    {

        GameObject prefab = Resources.Load<GameObject>(prefabName);

        if (prefab != null)
        {

            GameObject newObject = Instantiate(prefab, position, Quaternion.Euler(rotation));

            newObject.name = newObjectName;
            Debug.Log("Object " + newObjectName + " spawned at " + position + " with rotation " + rotation);
        }
        else
        {
            Debug.LogError("Prefab " + prefabName + " not found");
        }
    }

}
