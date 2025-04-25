import qrcode

url = "https://doc-finder-ecru.vercel.app/"
img = qrcode.make(url)
img.save("docfinder_qr.png")
