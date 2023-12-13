import os
import threading
from flask import Flask, request, render_template, send_file
from skimage.metrics import peak_signal_noise_ratio as psnr
import cv2
import numpy as np


app = Flask(__name__)



def run_app():
  app.run(host='0.0.0.0', port=8080)
# // homepage
# route


@app.route('/')
def home():
    return render_template('index.html')

# // image
# upload and process
# route




@app.route('/process', methods=['GET', 'POST'])
def process():
    # 1. Get uploaded image
    file = request.files['image']
    img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    # 2. Apply 5 filters
    gaussian = cv2.GaussianBlur(img, (5, 5), 0)
    median = cv2.medianBlur(img, 3)
    order_stats = cv2.filter2D(img, -1, kernel=np.ones((5, 5), np.float32) / 25)
    img1 = img
    if img1.dtype not in [np.uint8, np.float32]:
        img1 = img1.astype(np.uint8)
    bilateral = cv2.bilateralFilter(img1, 9, 75, 75)
    mean = cv2.blur(img, (5, 5))
    # # 3. Evaluate filters - PSNR, SSIM etc.
    # psnr_values = [psnr(img, filtered_img) for filtered_img in [gaussian, median, mean, order_stats, bilateral]]

    filtered_imgs = {
        'original': img,
        'gaussian': gaussian,
        'median': median,
        'mean' :mean,
        'bilateral' : bilateral,
        'order_stats': order_stats
    }

    psnrs = {
        'gaussian': psnr(img, gaussian),
        'median': psnr(img, median),
        'mean': psnr(img, mean),
        'bilateral': psnr(img, bilateral),
        'order_stats': psnr(img, order_stats)
    }

    best_psnr = max(psnrs.values())
    best_filter = [f for f, p in psnrs.items() if p == best_psnr][0]
    # Get image from filtered_imgs dict
    print(type(best_filter))



    best_psnr = psnrs[best_filter]
    best_img = filtered_imgs[best_filter]
    # Create a dict with best filter details
    best = {
        'name': best_filter,
        'psnr': best_psnr,
        'img': './static/' + str(best_filter) + '.jpg'
    }
    print(best_img)
    print("++++")
    print(median)
    # Save best image
    cv2.imwrite('./static/' + str(best_filter) + '.jpg', best_img)

    # Pass only best filter details to template
    return render_template('results.html', best=best)



if __name__ == "__main__":

    t = threading.Thread(target=run_app)
    t.start()