using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Linq;
using UnityEngine.AI;
using UnityEngine.UI;
using System;

public class CameraController : MonoBehaviour
{

    public LayerMask targetLayer;
    public float maxDistance = 1.0f;

    public List<string> getObjectsInView(Camera camera)
    {
        Debug.Log("Starting getObjectsInView method...");

        if (camera == null)
        {
            Debug.LogError("Camera is null.");
            return new List<string>();
        }

        GameObject PickUpableParent = SafeFind("PickUpableObjects");
        GameObject MoveableParent = SafeFind("MoveableObjects");
        GameObject StaticParent = SafeFind("StaticObjects");

        List<GameObject> InViewObjects = new List<GameObject>();
        List<string> InViewObjectsString = new List<string>();

        try
        {

            ProcessParentObjects(PickUpableParent, "PickUpableObjects", camera, InViewObjects, InViewObjectsString);
            ProcessParentObjects(MoveableParent, "MoveableObjects", camera, InViewObjects, InViewObjectsString);
            ProcessParentObjects(StaticParent, "StaticObjects", camera, InViewObjects, InViewObjectsString);

            Debug.Log($"Total objects in view: {InViewObjectsString.Count}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"An exception occurred: {ex.Message}\n{ex.StackTrace}");
        }

        Debug.Log("Finished getObjectsInView method.");
        return InViewObjectsString;
    }

    private GameObject SafeFind(string name)
    {
        GameObject obj = GameObject.Find(name);
        if (obj == null)
        {
            Debug.LogError($"GameObject '{name}' not found.");
        }
        else
        {
            Debug.Log($"GameObject '{name}' found successfully.");
        }
        return obj;
    }

    private void ProcessParentObjects(GameObject parent, string parentName, Camera camera, List<GameObject> InViewObjects, List<string> InViewObjectsString)
    {
        if (parent != null)
        {
            Debug.Log($"Processing parent object: {parentName}");
            List<GameObject> childObjects = GetFirstLevelActiveChildren(parent);

            if (childObjects == null || childObjects.Count == 0)
            {
                Debug.LogWarning($"No active children found under parent {parentName}.");
                return;
            }

            foreach (GameObject child in childObjects)
            {
                if (child == null)
                {
                    Debug.LogError($"Null reference encountered in children of {parentName}.");
                    continue;
                }

                if (IsObjectInCamera(camera, child))
                {
                    Debug.Log($"We can see {child.name} from {parentName}.");
                    InViewObjects.Add(child);
                    InViewObjectsString.Add(child.name);
                }
            }
        }
        else
        {
            Debug.LogError($"GameObject '{parentName}' not found.");
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
        Renderer[] objRenderers = obj.GetComponentsInChildren<Renderer>();

        if (objRenderers == null)
        {
            Debug.LogError($"{obj.name} does not have a Renderer component.");
            return false;
        }

        foreach (Renderer objRenderer in objRenderers)
        {

            Plane[] planes = GeometryUtility.CalculateFrustumPlanes(displayCamera);
            if (GeometryUtility.TestPlanesAABB(planes, objRenderer.bounds))
            {
                Debug.Log("### TestPlanesAABB true  " + obj.name);

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

                foreach (var point in pointsToCheck)
                {

                    if (IsPointVisible(displayCamera, point, obj))
                    {
                        return true;
                    }
                }
            }        
        }

        return false;
    }

    Vector3 GetTwoThirdsPoint(Vector3 start, Vector3 end)
    {
        return start + (2f / 3f) * (end - start);
    }

    bool IsPointVisible(Camera cam, Vector3 point, GameObject obj)
    {

        if (cam == null)
        {
            Debug.LogError("Camera is null in IsPointVisible.");
            return false;
        }

        if (obj == null)
        {
            Debug.LogError("GameObject 'obj' is null in IsPointVisible.");
            return false;
        }

        Debug.Log($"Checking visibility of point {point} for object {obj.name} using camera {cam.name}.");

        Vector3 viewportPoint;
        try
        {
            viewportPoint = cam.WorldToViewportPoint(point);
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred in WorldToViewportPoint: {ex.Message}");
            return false;
        }

        bool isInFrustum = viewportPoint.z > 0 &&
                           viewportPoint.x >= 0 && viewportPoint.x <= 1 &&
                           viewportPoint.y >= 0 && viewportPoint.y <= 1;
        if (!isInFrustum)
        {
            Debug.Log($"Point {point} is outside the camera's view frustum.");
            return false;
        }

        RaycastHit hit;

        try
        {
            if (Physics.Raycast(cam.transform.position, point - cam.transform.position, out hit, Mathf.Infinity, targetLayer))
            {
                Debug.Log($"Raycast hit object: {hit.transform.name}");

                if (hit.transform.parent != null)
                {
                    Debug.Log($"Hit object's parent: {hit.transform.parent.name}");
                    if (hit.transform.parent.name == obj.name)
                    {
                        Debug.Log($"Visibility check passed: hit parent {hit.transform.parent.name} matches object {obj.name}.");
                        return true;
                    }
                }
                else
                {
                    Debug.LogWarning("Hit object's parent is null.");
                }

                if (hit.transform.name == obj.name)
                {
                    Debug.Log($"Visibility check passed: hit object {hit.transform.name} matches object {obj.name}.");
                    return true;
                }
            }
            else
            {
                Debug.Log("Raycast did not hit any object.");
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Exception occurred during Raycast: {ex.Message}");
            return false;
        }

        Debug.Log($"Visibility check failed for point {point} and object {obj.name}.");
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
