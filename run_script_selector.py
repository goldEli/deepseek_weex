#!/usr/bin/env python3
import os
import re
import subprocess
import sys

def parse_script_file(script_file_path):
    """从SCRIPT.md文件中解析出命令"""
    commands = []
    descriptions = []
    
    try:
        with open(script_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 提取shell块中的内容
            shell_content = re.search(r'```shell\n(.*?)```', content, re.DOTALL)
            if shell_content:
                lines = shell_content.group(1).strip().split('\n')
                current_desc = ""
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 检查是否是注释行（描述）
                    if line.startswith('#'):
                        current_desc = line.lstrip('#').strip()
                    # 检查是否是执行命令行
                    elif line.startswith(('uv run', 'python', 'python3')):
                        # 移除行尾的分号
                        command = line.rstrip(';')
                        commands.append(command)
                        descriptions.append(current_desc)
    
    except Exception as e:
        print(f"解析脚本文件时出错: {e}")
        return [], []
    
    return commands, descriptions

def execute_command(command):
    """执行命令并显示输出"""
    print(f"\n正在执行命令: {command}")
    print("=" * 60)
    
    try:
        # 使用shell=True来支持更复杂的命令
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # 实时显示输出
        for stdout_line in iter(process.stdout.readline, ""):
            print(stdout_line, end="")
        
        for stderr_line in iter(process.stderr.readline, ""):
            print(stderr_line, end="", file=sys.stderr)
        
        process.wait()
        
        if process.returncode == 0:
            print("\n命令执行成功!")
        else:
            print(f"\n命令执行失败，返回码: {process.returncode}")
            
    except Exception as e:
        print(f"执行命令时出错: {e}")
    
    print("=" * 60)

def main():
    """主函数"""
    script_file = os.path.join(os.path.dirname(__file__), 'SCRIPT.md')
    
    if not os.path.exists(script_file):
        print(f"错误: 找不到文件 {script_file}")
        sys.exit(1)
    
    commands, descriptions = parse_script_file(script_file)
    
    if not commands:
        print("没有找到可执行的命令")
        sys.exit(1)
    
    # 显示菜单
    print("=== 脚本选择器 ===\n")
    print("可用的脚本命令:")
    for i, (command, desc) in enumerate(zip(commands, descriptions), 1):
        print(f"{i}. {desc}")
        print(f"   命令: {command}")
    print(f"{len(commands) + 1}. 执行所有脚本")
    print(f"{len(commands) + 2}. 退出\n")
    
    # 获取用户选择
    while True:
        try:
            choice = input(f"请选择要执行的脚本 (1-{len(commands) + 2}): ").strip()
            choice = int(choice)
            
            if 1 <= choice <= len(commands):
                # 执行单个脚本
                execute_command(commands[choice - 1])
                break
            elif choice == len(commands) + 1:
                # 执行所有脚本
                for command in commands:
                    execute_command(command)
                break
            elif choice == len(commands) + 2:
                # 退出
                print("退出程序")
                sys.exit(0)
            else:
                print("无效的选择，请重新输入")
                
        except ValueError:
            print("请输入有效的数字")

if __name__ == "__main__":
    main()
