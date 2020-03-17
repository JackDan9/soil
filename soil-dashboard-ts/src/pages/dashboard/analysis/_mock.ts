import moment from 'moment';
import { AnalysisData, RadarData, VisitDataType, ProfitData } from './data.d';

// mock data
const visitData: VisitDataType[] = [];
const beginDay = new Date().getTime();

const fakeY = [7, 5, 4, 2, 4, 7, 5, 6, 5, 9, 6, 3, 1, 5, 3, 6, 5];
for (let i = 0; i < fakeY.length; i += 1) {
  visitData.push({
    x: moment(new Date(beginDay + 1000 * 60 * 60 * 24 * i)).format('YYYY-MM-DD'),
    y: fakeY[i],
  });
}

const visitData2 = [];
const fakeY2 = [1, 6, 4, 8, 3, 7, 2];
for (let i = 0; i < fakeY2.length; i += 1) {
  visitData2.push({
    x: moment(new Date(beginDay + 1000 * 60 * 60 * 24 * i)).format('YYYY-MM-DD'),
    y: fakeY2[i],
  });
}

// const salesData = [];
// for (let i = 0; i < 12; i += 1) {
  // salesData.push({
    // x: `${i + 1}月`,
    // y: Math.floor(Math.random() * 1000) + 200,
  // });
// }
const searchData = [];
for (let i = 0; i < 50; i += 1) {
  searchData.push({
    index: i + 1,
    keyword: `搜索关键词-${i}`,
    count: Math.floor(Math.random() * 1000),
    range: Math.floor(Math.random() * 100),
    status: Math.floor((Math.random() * 10) % 2),
  });
}
const salesTypeData = [
  {
    x: '家用电器',
    y: 4544,
  },
  {
    x: '食用酒水',
    y: 3321,
  },
  {
    x: '个护健康',
    y: 3113,
  },
  {
    x: '服饰箱包',
    y: 2341,
  },
  {
    x: '母婴产品',
    y: 1231,
  },
  {
    x: '其他',
    y: 1231,
  },
];

const salesTypeDataOnline = [
  {
    x: '家用电器',
    y: 244,
  },
  {
    x: '食用酒水',
    y: 321,
  },
  {
    x: '个护健康',
    y: 311,
  },
  {
    x: '服饰箱包',
    y: 41,
  },
  {
    x: '母婴产品',
    y: 121,
  },
  {
    x: '其他',
    y: 111,
  },
];

const salesTypeDataOffline = [
  {
    x: '家用电器',
    y: 99,
  },
  {
    x: '食用酒水',
    y: 188,
  },
  {
    x: '个护健康',
    y: 344,
  },
  {
    x: '服饰箱包',
    y: 255,
  },
  {
    x: '其他',
    y: 65,
  },
];

const offlineData = [];
for (let i = 0; i < 10; i += 1) {
  offlineData.push({
    name: `Stores ${i}`,
    cvr: Math.ceil(Math.random() * 9) / 10,
  });
}
const offlineChartData = [];
for (let i = 0; i < 20; i += 1) {
  offlineChartData.push({
    x: new Date().getTime() + 1000 * 60 * 30 * i,
    y1: Math.floor(Math.random() * 100) + 10,
    y2: Math.floor(Math.random() * 100) + 10,
  });
}

const radarOriginData = [
  {
    name: '个人',
    ref: 10,
    koubei: 8,
    output: 4,
    contribute: 5,
    hot: 7,
  },
  {
    name: '团队',
    ref: 3,
    koubei: 9,
    output: 6,
    contribute: 3,
    hot: 1,
  },
  {
    name: '部门',
    ref: 4,
    koubei: 1,
    output: 6,
    contribute: 5,
    hot: 7,
  },
];

const radarData: RadarData[] = [];
const radarTitleMap = {
  ref: '引用',
  koubei: '口碑',
  output: '产量',
  contribute: '贡献',
  hot: '热度',
};
radarOriginData.forEach(item => {
  Object.keys(item).forEach(key => {
    if (key !== 'name') {
      radarData.push({
        name: item.name,
        label: radarTitleMap[key],
        value: item[key],
      });
    }
  });
});

const profitOriginData = {
	"msg": "",
	"status": 0,
	"data": {
		"1568304000": 62.57,
		"1566921600": 11433.42,
		"1563638400": 14764.86,
		"1565539200": 13286.22,
		"1563552000": 20572.81,
		"1568131200": 18259.96,
		"1567612800": 16286.09,
		"1566662400": 7803.7,
		"1565798400": 16878.42,
		"1566403200": 18935.4,
		"1567958400": 16510.5,
		"1567353600": 12756.84,
		"1567526400": 24237.88,
		"1563897600": 18305.15,
		"1565107200": 10952.42,
		"1565884800": 18244.09,
		"1564070400": 17701.63,
		"1565625600": 15998.89,
		"1568044800": 24680.94,
		"1567785600": 10493.58,
		"1565366400": 4553.79,
		"1567180800": 9972.19,
		"1567872000": 10913.43,
		"1563120000": 12380.93,
		"1563379200": 14744.99,
		"1563206400": 16920.58,
		"1566057600": 16722.89,
		"1567440000": 12874.86,
		"1567267200": 12488.96,
		"1567699200": 12124.3,
		"1565971200": 14719.18,
		"1567094400": 15615.38,
		"1563292800": 14110.76,
		"1564156800": 12994.67,
		"1564243200": 10303.15,
		"1566835200": 12254.89,
		"1564502400": 12298.42,
		"1563724800": 17666.05,
		"1566748800": 12026.67,
		"1563811200": 17642.37,
		"1564675200": 14902.74,
		"1566230400": 16848.09,
		"1565712000": 13565.89,
		"1566489600": 13621.06,
		"1566316800": 20140.92,
		"1566576000": 12023.91,
		"1566144000": 20072.57,
		"1564761600": 16470.11,
		"1563465600": 15167.67,
		"1564416000": 17282.86,
		"1567008000": 10907.36,
		"1564934400": 14179.96,
		"1563984000": 19643.21,
		"1564588800": 12474.41,
		"1565280000": 12360.03,
		"1564848000": 18067.51,
		"1564329600": 14749.98,
		"1565193600": 13647.69,
		"1568217600": 4715.07,
		"1565020800": 10707.22,
		"1565452800": 11661.75
	}
}

const profitData: ProfitData[] = [];

function getLocaleTime(nS: any) {
  return new Date(parseInt(nS) * 1000).toLocaleString('en-GB', { timeZone: 'UTC' });
}
Object.keys(profitOriginData['data']).forEach(key => {
  profitData.push({
    name: getLocaleTime(key),
    value: profitOriginData['data'][key]
  })
})

const salesData = [];
Object.keys(profitOriginData['data']).forEach(key => {
  salesData.push({
    x: getLocaleTime(key),
    y: profitOriginData['data'][key]
  });
})
// profitData.push(profitOriginData['data']);

const getFakeChartData: AnalysisData = {
  visitData,
  visitData2,
  searchData,
  offlineData,
  offlineChartData,
  salesTypeData,
  salesTypeDataOnline,
  salesTypeDataOffline,
  radarData,
  profitData,
  salesData
};

export default {
  'GET  /api/fake_chart_data': getFakeChartData,
};
