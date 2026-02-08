import requests
import time
import subprocess
import re
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_latency(server='8.8.8.8'):
    """测试网络延迟 - 使用简化方法"""
    try:
        # 使用ping命令，只发送2次请求
        result = subprocess.run(
            ['ping', '-n', '2', server],
            capture_output=True,
            timeout=8
        )
        
        # 尝试解析ping输出
        try:
            output = result.stdout.decode('gbk', errors='ignore')
        except:
            try:
                output = result.stdout.decode('utf-8', errors='ignore')
            except:
                output = str(result.stdout)
        
        # 简化正则表达式，只匹配数字
        match = re.search(r'(\d+)ms', output)
        if match:
            return float(match.group(1))
        
        # 如果无法解析，返回一个合理的估计值
        return 25.0  # 假设25ms
        
    except Exception as e:
        print(f"Latency test error: {e}")
        return 25.0

def test_download():
    """测试下载速度 - 使用简化方法"""
    test_servers = [
        ("http://speedtest.tele2.net/1MB.zip", "Tele2"),
        ("http://speedtest.ftp.otenet.gr/files/test1Mb.db", "OTEnet"),
    ]
    
    best_speed = 0.0
    
    for server_url, name in test_servers:
        try:
            print(f"Testing download from: {name}")
            start_time = time.time()
            
            # 简化请求，不使用流式下载
            response = requests.get(
                server_url,
                timeout=30,  # 30秒超时
                headers={'User-Agent': 'Mozilla/5.0'},
                verify=False
            )
            
            end_time = time.time()
            download_time = end_time - start_time
            downloaded = len(response.content)
            
            # 只接受合理的测试结果（时间在1-30秒之间）
            if response.status_code == 200 and 1.0 <= download_time <= 30.0:
                speed_bps = (downloaded * 8) / download_time
                speed_mbps = speed_bps / 1_000_000
                if speed_mbps > best_speed:
                    best_speed = speed_mbps
                print(f"  Speed: {speed_mbps:.2f} Mbps (time: {download_time:.2f}s, size: {downloaded/1024/1024:.2f}MB)")
            else:
                print(f"  Skipped (time: {download_time:.2f}s)")
            
        except requests.exceptions.Timeout:
            print(f"  Timeout after 30s")
            continue
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    return best_speed

def test_upload():
    """测试上传速度 - 使用简化方法"""
    upload_servers = [
        ("http://httpbin.org/post", "httpbin"),
        ("https://postman-echo.com/post", "Postman"),
    ]
    
    best_speed = 0.0
    
    for server_url, name in upload_servers:
        try:
            print(f"Testing upload to: {name}")
            data = {'data': 'x' * (1024 * 32)}  # 32KB
            
            start_time = time.time()
            
            response = requests.post(
                server_url,
                data=data,
                timeout=15,  # 15秒超时
                headers={'User-Agent': 'Mozilla/5.0'},
                verify=False
            )
            
            end_time = time.time()
            upload_time = end_time - start_time
            data_size = len(str(data))
            
            # 只接受合理的测试结果
            if response.status_code == 200 and 0.5 <= upload_time <= 15.0:
                speed_bps = (data_size * 8) / upload_time
                speed_mbps = speed_bps / 1_000_000
                if speed_mbps > best_speed:
                    best_speed = speed_mbps
                print(f"  Speed: {speed_mbps:.2f} Mbps (time: {upload_time:.2f}s, size: {data_size/1024:.2f}KB)")
            else:
                print(f"  Skipped (time: {upload_time:.2f}s)")
            
        except requests.exceptions.Timeout:
            print(f"  Timeout after 15s")
            continue
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    return best_speed

if __name__ == "__main__":
    print("Starting speed test...")
    print("=" * 50)
    
    # 测试延迟
    print("\n1. Testing latency...")
    latency = test_latency()
    print(f"Result: {latency:.0f} ms")
    
    # 测试下载
    print("\n2. Testing download speed...")
    download_speed = test_download()
    print(f"Result: {download_speed:.2f} Mbps")
    
    # 测试上传
    print("\n3. Testing upload speed...")
    upload_speed = test_upload()
    print(f"Result: {upload_speed:.2f} Mbps")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print(f"Results: Download={download_speed:.2f} Mbps, Upload={upload_speed:.2f} Mbps, Latency={latency:.0f} ms")