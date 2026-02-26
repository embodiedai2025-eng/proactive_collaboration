using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Linq;
using UnityEngine.AI;
using UnityEngine.UI;
using System;

public class CameraControllerDemo : MonoBehaviour
{
    public Camera nowcam;
    public LayerMask targetLayer;
    public float maxDistance = 1.0f;

    List<String> getObjectsInView(Camera camera)
    {
        GameObject PickUpableParent = GameObject.Find("PickUpableObjects");
        GameObject MoveableParent = GameObject.Find("MoveableObjects");
        GameObject StaticParent = GameObject.Find("StaticObjects");
        GameObject ObjectParent = GameObject.Find("Objects");
        List<GameObject> InViewObjects = new List<GameObject>();
        List<String> InViewObjectsString = new List<String>();
        GameObject[] allGameObjects = FindObjectsOfType<GameObject>();
        List<GameObject> robots = new List<GameObject>();
        foreach (GameObject obj in allGameObjects)
        {

            if (obj.name.StartsWith("Robot"))
            {
                robots.Add(obj);
                Debug.Log("Found Robot: " + obj.name);
            }
        }
        foreach (GameObject rob in robots)
        {

            Renderer[] objRenderers = rob.GetComponentsInChildren<Renderer>();
            foreach (Renderer objRenderer in objRenderers)
            {

                Plane[] planes = GeometryUtility.CalculateFrustumPlanes(camera);
                if (GeometryUtility.TestPlanesAABB(planes, objRenderer.bounds))
                {
                    InViewObjects.Add(rob);
                    InViewObjectsString.Add(rob.name);
                    break;
                }
            }
        }
        if (PickUpableParent != null)
        {

            List<GameObject> PickUpableObjects = GetFirstLevelActiveChildren(PickUpableParent);
            foreach (GameObject child in PickUpableObjects)
            {

                if (IsObjectInCamera(camera, child))
                {
                    Debug.Log("We can see PickUpableObjects: " + child.name);
                    InViewObjects.Add(child);
                    InViewObjectsString.Add(child.name);

                }
            }
        }
        else
        {
            Debug.LogError("GameObject 'PickUpableObjects' not found.");
        }
        if (MoveableParent != null)
        {

            List<GameObject> MoveableObjects = GetFirstLevelActiveChildren(MoveableParent);
            foreach (GameObject child in MoveableObjects)
            {

                if (IsObjectInCamera(camera, child))
                {
                    Debug.Log("We can see MoveableObjects: " + child.name);
                    InViewObjects.Add(child);
                    InViewObjectsString.Add(child.name);
                }
            }
        }
        else
        {
            Debug.LogError("GameObject 'MoveableObjects' not found.");
        }
        if (StaticParent != null)
        {

            List<GameObject> StaticObjects = GetFirstLevelActiveChildren(StaticParent);
            foreach (GameObject child in StaticObjects)
            {

                if (IsObjectInCamera(camera, child))
                {
                    Debug.Log("We can see StaticObjects: " + child.name);
                    InViewObjects.Add(child);
                    InViewObjectsString.Add(child.name);
                }
            }
        }
        else
        {
            Debug.LogError("GameObject 'StaticObjects' not found.");
        }
        if (ObjectParent != null)
        {

            List<GameObject> Objects = GetFirstLevelActiveChildren(ObjectParent);
            foreach (GameObject child in Objects)
            {

                if (IsObjectInCamera(camera, child))
                {
                    Debug.Log("We can see NormalObjects: " + child.name);
                    InViewObjects.Add(child);
                    InViewObjectsString.Add(child.name);
                }
            }
        }
        else
        {
            Debug.LogError("GameObject 'Objects' not found.");
        }

        return InViewObjectsString;

    }
    void OnDisable()
    {   

        List<String> res = getObjectsInView(nowcam);
        foreach (string s in res)
        {
            Debug.Log("!!!See Objects: " + s);
        }
    }

    void FindNeighborsWithRaycast(GameObject targetObject)
    {
        Vector3 position = targetObject.transform.position;
        Vector3[] directions = { Vector3.forward, Vector3.back, Vector3.left, Vector3.right, Vector3.up, Vector3.down };

        foreach (Vector3 direction in directions)
        {
            if (Physics.Raycast(position, direction, out RaycastHit hit, maxDistance))
            {
                if (hit.collider.gameObject != targetObject)
                {
                    if (hit.collider.gameObject.name != "mesh")
                    {
                        Debug.Log(targetObject.name + "  Neighbor found in direction " + direction + ": " + hit.collider.gameObject.name);
                    }else {
                        Debug.Log(targetObject.name + "  Neighbor found in direction " + direction + ": " + hit.collider.gameObject.transform.parent.name);
                    }                    
                }
            }
        }
    }

    public bool IsObjectInCamera(Camera displayCamera, GameObject obj)
    {

        if (displayCamera == null)
        {
            Debug.LogError("Display camera is null in IsObjectInCamera.");
            return false;
        }

        if (obj == null)
        {
            Debug.LogError("GameObject 'obj' is null in IsObjectInCamera.");
            return false;
        }

        Debug.Log($"Checking if object {obj.name} is in camera view: {displayCamera.name}");

        Renderer[] objRenderers = obj.GetComponentsInChildren<Renderer>();

        if (objRenderers == null || objRenderers.Length == 0)
        {
            Debug.LogError($"{obj.name} does not have any Renderer components.");
            return false;
        }

        Debug.Log($"Found {objRenderers.Length} renderers for object {obj.name}.");

        foreach (Renderer objRenderer in objRenderers)
        {
            if (objRenderer == null)
            {
                Debug.LogError($"A Renderer in object {obj.name} is null.");
                continue;
            }

            Plane[] planes;
            try
            {
                planes = GeometryUtility.CalculateFrustumPlanes(displayCamera);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Exception occurred in CalculateFrustumPlanes: {ex.Message}");
                return false;
            }

            if (GeometryUtility.TestPlanesAABB(planes, objRenderer.bounds))
            {
                Debug.Log($"Object {obj.name} is within the frustum of camera {displayCamera.name}.");

                Bounds bounds = objRenderer.bounds;
                List<Vector3> pointsToCheck = new List<Vector3>
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

                Transform[] childTransforms = obj.GetComponentsInChildren<Transform>();
                foreach (var childTransform in childTransforms)
                {
                    if (childTransform != null)
                    {
                        pointsToCheck.Add(childTransform.position);
                        Debug.Log($"Added child position: {childTransform.position} from object {childTransform.name}.");
                    }
                    else
                    {
                        Debug.LogWarning($"A child transform in {obj.name} is null.");
                    }
                }

                Debug.Log($"Checking visibility of {pointsToCheck.Count} points for object {obj.name}.");

                foreach (var point in pointsToCheck)
                {
                    Debug.Log($"Checking point {point} for object {obj.name}.");
                    try
                    {
                        if (IsPointVisible(displayCamera, point, obj))
                        {
                            Debug.Log($"Point {point} of object {obj.name} is visible.");
                            return true;
                        }
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"Exception occurred while checking point {point}: {ex.Message}");
                    }
                }
            }
            else
            {
                Debug.Log($"Object {obj.name} is not within the frustum of camera {displayCamera.name}.");
            }
        }

        Debug.Log($"Object {obj.name} is not visible in the camera {displayCamera.name}.");
        return false;
    }

    Vector3 GetTwoThirdsPoint(Vector3 start, Vector3 end)
    {
        return start + (2f / 3f) * (end - start);
    }

    bool IsPointVisible(Camera cam, Vector3 point, GameObject obj)
    {
        Vector3 viewportPoint = cam.WorldToViewportPoint(point);

        bool isInFrustum = viewportPoint.z > 0 &&
                           viewportPoint.x >= 0 && viewportPoint.x <= 1 &&
                           viewportPoint.y >= 0 && viewportPoint.y <= 1;
        if (!isInFrustum)
        {
            return false;
        }
        RaycastHit hit;

        Debug.DrawRay(cam.transform.position, (point - cam.transform.position) * 100f, Color.red, 56f);

        if (Physics.Raycast(cam.transform.position, point - cam.transform.position, out hit, Mathf.Infinity, targetLayer))
        {

            if (hit.transform.parent.name != null)
            {
                if(hit.transform.parent.name == obj.name)
                {
                    return true;

                }
            }
            if (hit.transform.name == obj.name)
            {
                return true;

            }
        }
        return false;
    }

    List<GameObject> GetFirstLevelActiveChildren(GameObject obj)
    {
        List<GameObject> children = new List<GameObject>();

        foreach (Transform child in obj.transform)
        {
            if (child.gameObject.activeSelf == true)
            {
            children.Add(child.gameObject);
            }            
        }

        return children;
    }

}
