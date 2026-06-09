import json
from datetime import datetime

def analyze_data(records_json, profile_json):
    try:
        records = json.loads(records_json)
        profile = json.loads(profile_json)
    except Exception as e:
        return f"<p style='color:red;'>データの読み込みに失敗しました: {str(e)}</p>"

    if not records:
        return "<p class='text-slate-500'>分析に必要な体重データがまだ登録されていません。上のフォームから入力してください。</p>"

    height = float(profile.get('height', 0)) if profile.get('height') else None
    target_weight = float(profile.get('target', 0)) if profile.get('target') else None

    # 最新レコード
    latest_record = records[-1]
    latest_weight = float(latest_record['weight'])
    latest_waist = latest_record.get('waist')
    
    report_html = ""

    # 1. BMI分析
    if height:
        height_m = height / 100.0
        bmi = latest_weight / (height_m ** 2)
        appropriate_weight = (height_m ** 2) * 22.0
        
        if bmi < 18.5:
            status = "低体重 (痩せ型)"
            status_color = "text-amber-600"
        elif bmi < 25.0:
            status = "普通体重"
            status_color = "text-emerald-600"
        else:
            status = "肥満"
            status_color = "text-rose-600"

        report_html += f"""
        <div class="mb-4 bg-slate-50 p-3 rounded-xl border border-slate-100">
            <div class="font-bold text-xs text-slate-400 mb-1">📐 BMI分析</div>
            <div class="text-sm">最新BMI: <span class="font-bold">{bmi:.1f}</span> (<span class="{status_color} font-bold">{status}</span>)</div>
            <div class="text-xs text-slate-500 mt-1">あなたの適正体重: <span class="font-semibold">{appropriate_weight:.1f} kg</span></div>
        </div>
        """

    # 2. ウエスト（腹囲）の簡易評価
    if latest_waist is not None:
        latest_waist = float(latest_waist)
        first_waist = None
        for r in records:
            if r.get('waist') is not None:
                first_waist = float(r['waist'])
                break
        
        waist_report = f"""
        <div class="mb-4 bg-slate-50 p-3 rounded-xl border border-slate-100">
            <div class="font-bold text-xs text-slate-400 mb-1">📏 ウエスト分析</div>
            <div class="text-sm">最新値: <span class="font-bold text-slate-800">{latest_waist:.1f} cm</span></div>
        """
        
        if first_waist is not None and first_waist != latest_waist:
            waist_diff = latest_waist - first_waist
            w_trend = "📈" if waist_diff > 0 else "📉"
            w_color = "text-rose-500" if waist_diff > 0 else "text-emerald-600"
            waist_report += f"""
            <div class="text-xs mt-1">初日比: <span class="font-semibold {w_color}">{w_trend} {waist_diff:+.1f} cm</span></div>
            """
        
        if latest_waist >= 85.0:
            waist_report += f"""
            <div class="text-[10px] text-amber-600 mt-1.5 font-medium">⚠️ 腹囲85cm以上は、内臓脂肪の蓄積に注意が必要な目安です。</div>
            """
        
        waist_report += "</div>"
        report_html += waist_report

    # 3. 目標体重とのギャップ
    if target_weight:
        diff = latest_weight - target_weight
        if diff > 0:
            report_html += f"""
            <div class="mb-4 bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div class="font-bold text-xs text-slate-400 mb-1">🎯 目標体重まで</div>
                <div class="text-md font-bold text-rose-500">あと +{diff:.1f} kg</div>
            </div>
            """
        elif diff <= 0:
            report_html += f"""
            <div class="mb-4 bg-emerald-50 p-3 rounded-xl border border-emerald-100">
                <div class="font-bold text-xs text-emerald-600 mb-1">🎉 目標クリア！</div>
                <div class="text-sm text-emerald-800">目標体重を維持できています（差分: {diff:.1f} kg）</div>
            </div>
            """

    # 4. 体重の通算傾向と予測
    if len(records) >= 2:
        weights = [float(r['weight']) for r in records]
        total_diff = latest_weight - weights[0]
        trend_symbol = "📈" if total_diff > 0 else "📉"
        trend_color = "text-rose-500" if total_diff > 0 else "text-emerald-600"

        report_html += f"""
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
            <div class="font-bold text-xs text-slate-400 mb-1">🏁 体重の通算傾向 (初日比)</div>
            <div class="text-sm flex items-center gap-1">
                <span>全体で</span>
                <span class="font-bold {trend_color}">{trend_symbol} {total_diff:+.1f} kg</span>
                <span>の変化</span>
            </div>
        </div>
        """

        if len(records) >= 5 and target_weight and latest_weight > target_weight:
            try:
                days = [(datetime.strptime(r['date'], "%Y-%m-%d") - datetime.strptime(records[0]['date'], "%Y-%m-%d")).days for r in records]
                if len(set(days)) > 1:
                    n = len(records)
                    sum_x = sum(days)
                    sum_y = sum(weights)
                    sum_xx = sum(x**2 for x in days)
                    sum_xy = sum(x*y for x, y in zip(days, weights))
                    
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
                    
                    if slope < 0:
                        days_needed = (target_weight - latest_weight) / slope
                        report_html += f"""
                        <div class="mt-4 p-3 bg-indigo-50 rounded-xl border border-indigo-100 text-xs text-indigo-900">
                            <strong>🔮 [PREDICTION] 達成予測</strong><br>
                            現在のペース（1日あたり 約 {-slope*1000:.0f}g 減少）を維持すると、あと <strong>{int(days_needed)}日</strong> で目標の {target_weight:.1f}kg に到達可能です。
                        </div>
                        """
                    else:
                        report_html += f"""
                        <div class="mt-4 p-3 bg-amber-50 rounded-xl border border-amber-100 text-xs text-amber-900">
                            <strong>⚠️ 推移アドバイス</strong><br>
                            体重が微増傾向、または横ばいにあります。食事や運動記録を少し見直してみましょう。
                        </div>
                        """
            except Exception as ex:
                pass

    return report_html
