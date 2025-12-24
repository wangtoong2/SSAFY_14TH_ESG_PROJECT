import {
  mdiAccountCircle,
  mdiMonitor,
  mdiGithub,
  mdiLock,
  mdiAlertCircle,
  mdiSquareEditOutline,
  mdiTable,
  mdiViewList,
  mdiTelevisionGuide,
  mdiResponsive,
  mdiPalette,
  mdiLogout,
} from '@mdi/js'

// 🔹 로그인 상태
export const menuAsideMainLogin = [
  {
    label: '대시보드',
    icon: mdiMonitor,
    to: '/',
  },
  {
    label: '프로필',
    icon: mdiAccountCircle,
    to: '/profile',
  },
  {
    label: '게시글',
    icon: mdiViewList,
    to: '/articlelist',
  },
  {
    label: '내 관심 기업',
    icon: mdiViewList,
    to: '/favorites',
  },
  {
    label: '로그아웃',
    icon: mdiLogout,
    isLogout: true,
    to: '/dashboard',
  },
]

// 🔹 비로그인 상태
export const menuAsideMainLogout = [
  {
    label: '로그인',
    icon: mdiLock,
    to: '/login',
  },
  {
    label: '회원가입',
    icon: mdiAccountCircle,
    to: '/signup',
  },
]

// 🔹 하단 메뉴 (공통)
// export const menuAsideBottom = [
//   {
//     label: 'Logout',
//     icon: mdiLogout,
//     isLogout: true,
//   },




// export const menuAsideMain = [
//   {
//     to: '/dashboard',
//     icon: mdiMonitor,
//     label: 'Dashboard',
//   },
//   {
//     to: '/create',
//     label: '글 작성',
//     icon: mdiTable,
//   },
//   {
//     to: '/login',
//     label: '로그인',
//     icon: mdiTable,
//   },
//   {
//     to: '/signuo',
//     label: '회원가입',
//     icon: mdiTable,
//   },
//   {
//     to: '/tables',
//     label: 'Tables',
//     icon: mdiTable,
//   },
//   {
//     to: '/forms',
//     label: 'Forms',
//     icon: mdiSquareEditOutline,
//   },
//   {
//     to: '/ui',
//     label: 'UI',
//     icon: mdiTelevisionGuide,
//   },
//   {
//     to: '/responsive',
//     label: 'Responsive',
//     icon: mdiResponsive,
//   },
//   {
//     to: '/',
//     label: 'Styles',
//     icon: mdiPalette,
//   },
//   {
//     to: '/profile',
//     label: 'Profile',
//     icon: mdiAccountCircle,
//   },
//   {
//     to: '/login',
//     label: 'Login',
//     icon: mdiLock,
//   },
//   {
//     to: '/error',
//     label: 'Error',
//     icon: mdiAlertCircle,
//   },
//   {
//     label: 'Dropdown',
//     icon: mdiViewList,
//     menu: [
//       {
//         label: 'Item One',
//       },
//       {
//         label: 'Item Two',
//       },
//     ],
//   },

// ]

export const menuAsideBottom = [
  {
    label: 'Logout',
    icon: mdiLogout,
    color: 'info',
    isLogout: true,
  },
]
