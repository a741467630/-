import socket


def port_scanner(ip, port_range):
    open_ports = []
    total_ports = len(port_range)
    print(f"开始扫描 {total_ports} 个端口...")
    for i, port in enumerate(port_range):
        try:
            print(f"\r正在扫描端口 {port} ({i+1}/{total_ports})...", end="")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
                print(f"\n发现开放端口: {port}")
            sock.close()
        except KeyboardInterrupt:
            print("\n扫描被用户中断，已扫描端口:", open_ports)
            return open_ports
        except socket.timeout:
            continue
        except Exception as e:
            print(f"\n扫描端口 {port} 时出错: {str(e)}")
            continue
    print("\n扫描完成！")
    return open_ports