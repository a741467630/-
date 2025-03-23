import psutil
import pandas as pd
from datetime import datetime
from port_scanner import port_scanner
import wmi


# 高危端口列表
HIGH_RISK_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3306, 3389, 5900, 8080]

def get_system_status():
    """获取系统状态信息"""
    status = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,

    }
    return status

def check_high_risk_ports(open_ports):
    """检查高危端口"""
    return [port for port in open_ports if port in HIGH_RISK_PORTS]

def get_port_solutions(ports):
    solutions = {
        21: '关闭FTP服务或使用SFTP替代',
        22: '限制SSH访问IP范围或使用密钥认证',
        23: '关闭Telnet服务，使用SSH替代',
        25: '配置SMTP认证，防止邮件中继滥用',
        53: '限制DNS区域传输，启用DNSSEC',
        80: '启用HTTPS，配置WAF防护',
        110: '启用POP3S加密',
        135: '关闭RPC服务或限制访问',
        139: '关闭NetBIOS服务',
        143: '启用IMAPS加密',
        443: '更新SSL/TLS证书，禁用弱加密协议',
        445: '关闭SMB服务或升级到最新版本',
        3306: '限制MySQL访问IP，修改默认端口',
        3389: '启用RDP网络级认证，限制访问IP',
        5900: '使用VNC加密或改用SSH隧道',
        8080: '关闭非必要Web服务或配置访问控制'
    }
    return '; '.join([solutions.get(port, '请检查此端口用途') for port in ports])


def generate_report(ip, open_ports, system_status):
    """生成报告"""
    high_risk_ports = check_high_risk_ports(open_ports)
    
    # 构建数据字典
    data = {
        'IP地址': ip,
        '时间戳': system_status['timestamp'],
        'CPU使用率(%)': system_status['cpu_usage'],
        '内存使用率(%)': system_status['memory_usage'],
        '磁盘使用率(%)': system_status['disk_usage'],
        '高危端口': [],
        '解决方案': [],
        '状态警告': '否'
    }
    
    if high_risk_ports:
        for port in high_risk_ports:
            data['高危端口'].append(port)
            data['解决方案'].append(get_port_solutions([port]))
            if any([system_status['cpu_usage'] > 90,
                   system_status['memory_usage'] > 90,
                   system_status['disk_usage'] > 90]):
                data['状态警告'] = '是'
    else:
        data['高危端口'].append('无')
        data['解决方案'].append('无')

    # 创建DataFrame并展开多值字段
    df = pd.DataFrame(data)
    if len(high_risk_ports) > 0:
        df = df.explode('高危端口').explode('解决方案')
    

    # 创建DataFrame并保存为Excel
    df = pd.DataFrame(data)
    filename = f"{ip}_系统监控报告_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    
    # 创建Excel writer对象
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='系统监控报告')
    
    # 获取工作簿和工作表对象
    workbook = writer.book
    worksheet = writer.sheets['系统监控报告']
    
    # 设置单元格格式
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    # 应用标题样式
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # 设置列宽
    worksheet.set_column(0, len(df.columns)-1, 20)
    
    # 保存文件
    writer.close()
    print(f"报告已生成：{filename}")

if __name__ == "__main__":
    ip = input("请输入目标IP地址: ").strip()
    
    # 获取系统状态
    system_status = get_system_status()
    
    # 端口扫描（使用现有端口扫描功能）
    open_ports = port_scanner(ip, range(1, 1025))
    
    # 生成报告
    generate_report(ip, open_ports, system_status)