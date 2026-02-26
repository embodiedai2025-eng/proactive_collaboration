using UnityEngine;
using UnityEngine.AI;

public class RuntimeNavMeshBaker : MonoBehaviour
{
    public NavMeshSurface[] navMeshSurfaces;
    void Start()
    {
        navMeshSurfaces = FindObjectsOfType<NavMeshSurface>();
        foreach (var surface in navMeshSurfaces)
        {
            surface.BuildNavMesh();
        }
    }
    void bakeSurfaces()
    {
        navMeshSurfaces = FindObjectsOfType<NavMeshSurface>();
        foreach (var surface in navMeshSurfaces)
            {
                surface.BuildNavMesh();
            }
    }

}
