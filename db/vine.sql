-- phpMyAdmin SQL Dump
-- version 4.6.4
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 06-09-2016 a las 01:14:06
-- Versión del servidor: 10.1.17-MariaDB
-- Versión de PHP: 7.0.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `vine`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `account`
--

CREATE TABLE `account` (
  `user` varchar(50) NOT NULL,
  `access_token` varchar(255) NOT NULL,
  `token_type` varchar(30) NOT NULL,
  `token_expiry` varchar(30) NOT NULL,
  `refresh_token` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `job`
--

CREATE TABLE `job` (
  `id` int(20) UNSIGNED NOT NULL,
  `settingsID` int(20) UNSIGNED DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `url` varchar(100) NOT NULL,
  `scrape_limit` int(11) UNSIGNED NOT NULL,
  `scrape` int(11) UNSIGNED NOT NULL,
  `next_scrape` int(11) UNSIGNED NOT NULL,
  `combine_limit` int(11) UNSIGNED NOT NULL,
  `combine` int(11) UNSIGNED NOT NULL,
  `next_combine` int(11) UNSIGNED NOT NULL,
  `date_limit` int(11) UNSIGNED NOT NULL,
  `status` tinyint(4) NOT NULL,
  `autoupload` tinyint(1) NOT NULL,
  `formula` text NOT NULL COMMENT 'This should not be used'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Scrape Jobs';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `job_account`
--

CREATE TABLE `job_account` (
  `jobID` int(20) UNSIGNED NOT NULL,
  `accountID` varchar(50) NOT NULL,
  `title` varchar(100) NOT NULL,
  `language` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `password`
--

CREATE TABLE `password` (
  `id` int(11) UNSIGNED NOT NULL,
  `pass` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `password`
--

INSERT INTO `password` (`id`, `pass`) VALUES
(1, '9f05aa4202e4ce8d6a72511dc735cce9');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `settings`
--

CREATE TABLE `settings` (
  `id` int(20) UNSIGNED NOT NULL,
  `scale_1` varchar(255) NOT NULL,
  `scale_2` varchar(255) NOT NULL,
  `text_x` varchar(255) NOT NULL,
  `text_y` varchar(255) NOT NULL,
  `text_size` int(11) UNSIGNED NOT NULL,
  `font_size` varchar(255) NOT NULL,
  `font_color` varchar(255) NOT NULL,
  `font_background_color` varchar(255) NOT NULL,
  `font` varchar(255) NOT NULL,
  `image` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `id` varchar(50) NOT NULL,
  `name` varchar(30) NOT NULL,
  `banned` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `video`
--

CREATE TABLE `video` (
  `id` int(20) UNSIGNED NOT NULL,
  `settingsID` int(20) UNSIGNED DEFAULT NULL,
  `source` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(4) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `video_account`
--

CREATE TABLE `video_account` (
  `videoID` int(20) UNSIGNED NOT NULL,
  `accountID` varchar(50) NOT NULL,
  `title` varchar(100) NOT NULL,
  `language` varchar(50) NOT NULL,
  `url` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vine`
--

CREATE TABLE `vine` (
  `id` varchar(35) NOT NULL,
  `userID` varchar(50) NOT NULL,
  `url` varchar(2083) NOT NULL,
  `title` text CHARACTER SET utf8mb4 NOT NULL,
  `views` int(20) UNSIGNED NOT NULL,
  `likes` int(20) UNSIGNED NOT NULL,
  `comments` int(20) UNSIGNED NOT NULL,
  `reposts` int(20) UNSIGNED NOT NULL,
  `date` datetime NOT NULL,
  `dbdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Vine videos';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vine_job`
--

CREATE TABLE `vine_job` (
  `jobID` int(20) UNSIGNED NOT NULL,
  `vineID` varchar(35) NOT NULL,
  `used` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vine_video`
--

CREATE TABLE `vine_video` (
  `vineID` varchar(35) NOT NULL,
  `videoID` int(20) UNSIGNED NOT NULL,
  `position` int(11) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `account`
--
ALTER TABLE `account`
  ADD PRIMARY KEY (`user`);

--
-- Indices de la tabla `job`
--
ALTER TABLE `job`
  ADD PRIMARY KEY (`id`),
  ADD KEY `settingsID` (`settingsID`);

--
-- Indices de la tabla `job_account`
--
ALTER TABLE `job_account`
  ADD PRIMARY KEY (`jobID`,`accountID`),
  ADD KEY `fk_ja_account` (`accountID`);

--
-- Indices de la tabla `password`
--
ALTER TABLE `password`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `settings`
--
ALTER TABLE `settings`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `video`
--
ALTER TABLE `video`
  ADD PRIMARY KEY (`id`),
  ADD KEY `settingsID` (`settingsID`) USING BTREE;

--
-- Indices de la tabla `video_account`
--
ALTER TABLE `video_account`
  ADD PRIMARY KEY (`videoID`,`accountID`),
  ADD KEY `fk_va_account` (`accountID`);

--
-- Indices de la tabla `vine`
--
ALTER TABLE `vine`
  ADD PRIMARY KEY (`id`),
  ADD KEY `userID` (`userID`);

--
-- Indices de la tabla `vine_job`
--
ALTER TABLE `vine_job`
  ADD PRIMARY KEY (`jobID`,`vineID`),
  ADD KEY `fk_vj_vine` (`vineID`);

--
-- Indices de la tabla `vine_video`
--
ALTER TABLE `vine_video`
  ADD PRIMARY KEY (`vineID`,`videoID`),
  ADD KEY `fk_vv_video` (`videoID`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `job`
--
ALTER TABLE `job`
  MODIFY `id` int(20) UNSIGNED NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT de la tabla `password`
--
ALTER TABLE `password`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT de la tabla `settings`
--
ALTER TABLE `settings`
  MODIFY `id` int(20) UNSIGNED NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT de la tabla `video`
--
ALTER TABLE `video`
  MODIFY `id` int(20) UNSIGNED NOT NULL AUTO_INCREMENT;
--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `job`
--
ALTER TABLE `job`
  ADD CONSTRAINT `fk_job_settings` FOREIGN KEY (`settingsID`) REFERENCES `settings` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `job_account`
--
ALTER TABLE `job_account`
  ADD CONSTRAINT `fk_ja_account` FOREIGN KEY (`accountID`) REFERENCES `account` (`user`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_ja_job` FOREIGN KEY (`jobID`) REFERENCES `job` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `video`
--
ALTER TABLE `video`
  ADD CONSTRAINT `fk_video_settings` FOREIGN KEY (`settingsID`) REFERENCES `settings` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `video_account`
--
ALTER TABLE `video_account`
  ADD CONSTRAINT `fk_va_account` FOREIGN KEY (`accountID`) REFERENCES `account` (`user`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_va_video` FOREIGN KEY (`videoID`) REFERENCES `video` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `vine`
--
ALTER TABLE `vine`
  ADD CONSTRAINT `fk_vine_user` FOREIGN KEY (`userID`) REFERENCES `user` (`id`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `vine_job`
--
ALTER TABLE `vine_job`
  ADD CONSTRAINT `fk_vj_job` FOREIGN KEY (`jobID`) REFERENCES `job` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_vj_vine` FOREIGN KEY (`vineID`) REFERENCES `vine` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `vine_video`
--
ALTER TABLE `vine_video`
  ADD CONSTRAINT `fk_vv_video` FOREIGN KEY (`videoID`) REFERENCES `video` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_vv_vine` FOREIGN KEY (`vineID`) REFERENCES `vine` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
