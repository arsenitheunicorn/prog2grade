from flask import Flask, render_template, request
from final_proj import almain as fcode
from final_proj import main as fincode

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def seite():
    if request.method == 'POST':
        vkid = str(request.form['vkid'])
        d1 = request.form['d1']
        d2 = request.form['d2']
#        try:
        pst, txt, bpar = fcode(vkid, d1, d2)
        if pst != '':
            freq, comss = fincode(pst, txt, bpar)
            return render_template('base.html', freq=freq, comss=comss)
        else:
            output = 'Где-то произошла ошибка! '
            output += 'Проверьте формат ввода '
            output += 'или поменяйте id vk\n'
            return render_template('base.html', output=output)
    else:
        return render_template('base.html')
        
if __name__ == "__main__":
    app.run(debug=True)