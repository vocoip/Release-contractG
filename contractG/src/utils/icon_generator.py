#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图标生成器模块 - 使用 PIL 创建简单的图标
"""

import os
from PIL import Image, ImageDraw

def generate_icons():
    """生成图标文件"""
    print("开始生成图标文件...")
    
    # 确保图标目录存在
    icon_dir = os.path.join('resources', 'icons')
    os.makedirs(icon_dir, exist_ok=True)
    print(f"图标目录: {icon_dir}")
    
    # 图标配置
    icons = {
        'add': {
            'color': '#4CAF50',  # 绿色
            'shape': 'plus'
        },
        'edit': {
            'color': '#2196F3',  # 蓝色
            'shape': 'pencil'
        },
        'delete': {
            'color': '#F44336',  # 红色
            'shape': 'trash'
        },
        'star': {
            'color': '#FFC107',  # 黄色
            'shape': 'star'
        }
    }
    
    success_count = 0
    error_count = 0
    
    # 生成每个图标
    for name, config in icons.items():
        icon_path = os.path.join(icon_dir, f'{name}.png')
        try:
            # 创建 24x24 像素的图标
            img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 解析颜色
            color = tuple(int(config['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
            
            # 根据形状绘制图标
            if config['shape'] == 'plus':
                # 绘制加号
                draw.rectangle((10, 6, 14, 18), fill=color)  # 垂直线
                draw.rectangle((6, 10, 18, 14), fill=color)  # 水平线
                
            elif config['shape'] == 'pencil':
                # 绘制铅笔
                points = [(6, 18), (18, 6), (15, 3), (3, 15)]
                draw.polygon(points, fill=color)
                
            elif config['shape'] == 'trash':
                # 绘制垃圾桶
                draw.rectangle((7, 6, 17, 18), fill=color)  # 主体
                draw.rectangle((5, 4, 19, 6), fill=color)   # 盖子
                draw.rectangle((10, 2, 14, 4), fill=color)  # 把手
                
            elif config['shape'] == 'star':
                # 绘制星星
                points = [
                    (12, 2),  # 顶点
                    (15, 9),
                    (22, 9),  # 右上
                    (17, 14),
                    (19, 21), # 右下
                    (12, 17),
                    (5, 21),  # 左下
                    (7, 14),
                    (2, 9),   # 左上
                    (9, 9)
                ]
                draw.polygon(points, fill=color)
            
            # 保存图标
            img.save(icon_path, 'PNG')
            print(f"✓ 成功生成图标: {name}.png")
            success_count += 1
            
        except Exception as e:
            print(f"✗ 生成图标失败 {name}.png: {str(e)}")
            error_count += 1
    
    print(f"\n生成完成! 成功: {success_count}, 失败: {error_count}")

if __name__ == '__main__':
    generate_icons() 