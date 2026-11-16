using UnityEngine;

public class CameraPlayerFollower:MonoBehaviour{
    public Transform player;
    private Vector3 offset=new Vector3(0,1,-10);
    public float followSpeed=5f;
    public BoxCollider2D bounds;//边界
    private Camera cam;
    private float halfHeight,halfWidth;
    void Start(){
        cam=GetComponent<Camera>();
        halfHeight=cam.orthographicSize;
        halfWidth=halfHeight*cam.aspect;
    }
    void LateUpdate(){
        Vector3 targetPos=player.position+offset;
        targetPos.x=Mathf.Clamp(targetPos.x,bounds.bounds.min.x+halfWidth,bounds.bounds.max.x-halfWidth);
        targetPos.y=Mathf.Clamp(targetPos.y,bounds.bounds.min.y+halfHeight,bounds.bounds.max.y-halfHeight);
        transform.position=Vector3.Lerp(transform.position,targetPos,followSpeed*Time.deltaTime);
    }
}
