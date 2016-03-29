-- phpMyAdmin SQL Dump
-- version 4.4.13.1deb1
-- http://www.phpmyadmin.net
--
-- Servidor: localhost
-- Tiempo de generación: 22-03-2016 a las 18:55:27
-- Versión del servidor: 5.6.28-0ubuntu0.15.10.1
-- Versión de PHP: 5.6.11-1ubuntu3.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `vine_test`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `job`
--

CREATE TABLE IF NOT EXISTS `job` (
  `id` bigint(20) NOT NULL,
  `url` varchar(100) DEFAULT NULL,
  `scrape_limit` int(11) NOT NULL DEFAULT '999',
  `scrape` int(11) NOT NULL,
  `next_scrape` int(11) NOT NULL,
  `combine_limit` int(11) NOT NULL,
  `combine` int(11) NOT NULL,
  `next_combine` int(11) NOT NULL,
  `date_limit` int(20) NOT NULL DEFAULT '0',
  `status` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `password`
--

CREATE TABLE IF NOT EXISTS `password` (
  `idpassword` int(11) NOT NULL,
  `pass` varchar(50) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `password`
--

INSERT INTO `password` (`idpassword`, `pass`) VALUES
(1, '9f05aa4202e4ce8d6a72511dc735cce9');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `settings`
--

CREATE TABLE IF NOT EXISTS `settings` (
  `id` int(10) NOT NULL,
  `scale_1` varchar(255) DEFAULT NULL,
  `scale_2` varchar(255) DEFAULT NULL,
  `text_x` varchar(255) DEFAULT NULL,
  `text_y` varchar(255) DEFAULT NULL,
  `text` varchar(255) DEFAULT NULL,
  `font_size` varchar(255) DEFAULT NULL,
  `font_color` varchar(255) DEFAULT NULL,
  `font_background_color` varchar(255) DEFAULT NULL,
  `font` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `script_status` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `settings`
--

INSERT INTO `settings` (`id`, `scale_1`, `scale_2`, `text_x`, `text_y`, `text`, `font_size`, `font_color`, `font_background_color`, `font`, `image`, `script_status`) VALUES
(1, '720+200:720', '720:720', '(main_w/2-text_w/2)', '(main_h)-50', 'Text here please', '32', 'black@1', 'white@1', 'FreeSerif.ttf', 'deadpool_by_chasejc-d4d3aoz.png', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `video`
--

CREATE TABLE IF NOT EXISTS `video` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `job` varchar(100) NOT NULL,
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `video_job`
--

CREATE TABLE IF NOT EXISTS `video_job` (
  `jobID` bigint(20) NOT NULL,
  `videoID` varchar(25) NOT NULL,
  `used` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vine`
--

CREATE TABLE IF NOT EXISTS `vine` (
  `id` bigint(20) NOT NULL,
  `vineID` varchar(25) CHARACTER SET utf8 NOT NULL,
  `url` varchar(2083) DEFAULT NULL,
  `title` text,
  `user` varchar(30) DEFAULT NULL,
  `views` bigint(20) NOT NULL DEFAULT '0',
  `likes` bigint(20) NOT NULL DEFAULT '0',
  `comments` int(11) NOT NULL DEFAULT '0',
  `reposts` int(11) NOT NULL DEFAULT '0',
  `date` datetime NOT NULL,
  `dbdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Vines videos stored';

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `job`
--
ALTER TABLE `job`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `url` (`url`),
  ADD UNIQUE KEY `url_2` (`url`);

--
-- Indices de la tabla `password`
--
ALTER TABLE `password`
  ADD PRIMARY KEY (`idpassword`);

--
-- Indices de la tabla `settings`
--
ALTER TABLE `settings`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `video`
--
ALTER TABLE `video`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `video_job`
--
ALTER TABLE `video_job`
  ADD PRIMARY KEY (`jobID`,`videoID`),
  ADD KEY `jobID` (`jobID`),
  ADD KEY `videoID` (`videoID`) USING BTREE;

--
-- Indices de la tabla `vine`
--
ALTER TABLE `vine`
  ADD PRIMARY KEY (`vineID`),
  ADD UNIQUE KEY `vineID` (`vineID`),
  ADD UNIQUE KEY `id` (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `job`
--
ALTER TABLE `job`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT de la tabla `password`
--
ALTER TABLE `password`
  MODIFY `idpassword` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT de la tabla `settings`
--
ALTER TABLE `settings`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT de la tabla `video`
--
ALTER TABLE `video`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT de la tabla `vine`
--
ALTER TABLE `vine`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;
--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `video_job`
--
ALTER TABLE `video_job`
  ADD CONSTRAINT `job` FOREIGN KEY (`jobID`) REFERENCES `job` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `video` FOREIGN KEY (`videoID`) REFERENCES `vine` (`vineID`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
