import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'Malgun Gothic'

labels = ['해석 가능성', '복잡성', '예측 정확도', '학습 속도']
models = {
    'Random Forest': [3, 2, 3.5, 2],
    'Logistic Regression': [3, 1, 1.5, 3],
    'Gradient Boosting': [2, 3, 4, 1]
}

angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

for model, values in models.items():
    values += values[:1]
    ax.fill(angles, values, alpha=0.25, label=model)
    ax.plot(angles, values, linewidth=0)  # 선을 없앰

ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=12)

ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), frameon=False)

plt.title('모델별 특성 비교 레이더 차트', size=15, color='black', y=1.1)

plt.show()
