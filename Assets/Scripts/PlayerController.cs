using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// 玩家水平移动。Y 轴速度完全交给 Rigidbody2D（重力 + 碰撞），
/// 这里只写 X 轴，所以按 W/S 不会让玩家飞起来。
/// 必须挂 BoxCollider2D 才能站在地面上，RequireComponent 会自动补上。
/// </summary>
[RequireComponent(typeof(Rigidbody2D), typeof(BoxCollider2D))]
public class PlayerController : MonoBehaviour
{
    public float moveSpeed = 5f;

    private Rigidbody2D rb;
    private Vector2 moveInput;

    // PlayerInput (Player/Move) 会调用这个方法
    public void Move(InputAction.CallbackContext context)
    {
        moveInput = context.ReadValue<Vector2>();
    }

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    private void FixedUpdate()
    {
        // 只改水平速度，竖直速度保留物理引擎当前的值（重力下落 / 落地后为 0）
        rb.linearVelocity = new Vector2(moveInput.x * moveSpeed, rb.linearVelocity.y);
    }
}
