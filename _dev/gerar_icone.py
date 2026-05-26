from PIL import Image, ImageDraw
import os

size = 256
bg = (224, 122, 95)  # #e07a5f terracota
img = Image.new('RGBA', (size, size), bg + (255,))
draw = ImageDraw.Draw(img)

# fundo arredondado
mask = Image.new('L', (size, size), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle([(0,0),(size-1,size-1)], radius=48, fill=255)
img.putalpha(mask)
draw = ImageDraw.Draw(img)

# livro aberto (forma simplificada)
cx, cy = size//2, size//2
w, h = 100, 120
x1, y1 = cx - w//2, cy - h//2
x2, y2 = cx + w//2, cy + h//2
mid = cx

# páginas (fundo branco)
draw.polygon([(x1,y1), (mid,y1+15), (mid,y2-15), (x1,y2)], fill=(255,255,255,230))
draw.polygon([(mid,y1+15), (x2,y1), (x2,y2), (mid,y2-15)], fill=(255,255,255,200))

# capas
draw.rectangle([(x1,y1), (x1+3,y2)], fill=(50,50,50,200))
draw.rectangle([(x2-3,y1), (x2,y2)], fill=(50,50,50,200))

# lombada
draw.rectangle([(mid-2,y1+10),(mid+2,y2-10)], fill=(80,80,80,180))

# linha divisória no meio
draw.line([(mid,y1+18),(mid,y2-18)], fill=(180,180,180,150), width=1)

os.makedirs('release', exist_ok=True)
img.save('release/biblioteca-icon.png')
print(f'Icon: {os.path.getsize("release/biblioteca-icon.png")} bytes')
