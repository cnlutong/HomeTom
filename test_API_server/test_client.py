"""测试脚本：验证 HomeAssistantClient 与测试服务器的连接

运行前确保测试服务器已启动:
    cd /Users/tong/Desktop/code/HomeTom
    python3 -m uvicorn test_API_server.main:app --port 8123

然后运行此脚本:
    python3 -m test_API_server.test_client
"""

import asyncio
import sys
sys.path.insert(0, '/Users/tong/Desktop/code/HomeTom')

from src.infrastructure.adapters import HomeAssistantClient


async def main():
    print("=" * 60)
    print("🧪 测试 HomeAssistantClient 与测试服务器")
    print("=" * 60)
    print()
    
    async with HomeAssistantClient(
        base_url="http://localhost:8123",
        access_token="test_token",
        timeout=10.0,
    ) as client:
        
        # 1. 检查连接
        print("1️⃣  检查连接...")
        if await client.check_connection():
            print("   ✅ 连接成功!")
        else:
            print("   ❌ 连接失败!")
            return
        print()
        
        # 2. 获取配置
        print("2️⃣  获取系统配置...")
        response = await client.get_config()
        if response.success:
            config = response.data.get("config")
            print(f"   📍 位置: {config.location_name}")
            print(f"   🔢 版本: {config.version}")
            print(f"   🧩 组件数: {len(config.components)}")
        print()
        
        # 3. 获取所有状态
        print("3️⃣  获取所有实体状态...")
        response = await client.get_all_states()
        if response.success:
            states = response.data["states"]
            print(f"   共 {len(states)} 个实体:")
            for state in states[:5]:  # 只显示前5个
                print(f"   • {state.entity_id}: {state.state}")
        print()
        
        # 4. 调用服务 - 开灯
        print("4️⃣  调用服务: 开灯...")
        response = await client.call_service(
            domain="light",
            service="turn_on",
            entity_id="light.living_room",
            data={"brightness": 200}
        )
        if response.success:
            print("   ✅ 服务调用成功!")
        print()
        
        # 5. 获取更新后的状态
        print("5️⃣  验证状态更新...")
        response = await client.get_state("light.living_room")
        if response.success:
            state_obj = response.data.get("state_object")
            print(f"   💡 light.living_room: {state_obj.state}")
            print(f"   🔆 亮度: {state_obj.attributes.get('brightness')}")
        print()
        
        # 6. 触发事件
        print("6️⃣  触发自定义事件...")
        response = await client.fire_event("test_event", {"source": "test_client"})
        if response.success:
            print("   ✅ 事件触发成功!")
        print()
        
        # 7. 渲染模板
        print("7️⃣  渲染模板...")
        response = await client.render_template(
            "温度是 {{ states('sensor.temperature') }}°C"
        )
        if response.success:
            print(f"   📝 结果: {response.data['result']}")
        print()
        
        # 8. 获取服务列表
        print("8️⃣  获取可用服务...")
        response = await client.get_services()
        if response.success:
            services = response.data["services"]
            print(f"   共 {len(services)} 个服务域:")
            for svc in services:
                print(f"   • {svc.domain}: {', '.join(svc.services[:3])}")
        print()
    
    print("=" * 60)
    print("✅ 所有测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
