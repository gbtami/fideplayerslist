package utils

import java.io._
import java.lang.System

import scala.io.Source

class Timer
{
	var t0=System.nanoTime()
	def elapsed:Double = (System.nanoTime() - t0)/1.0e9
}

object HeapSize
{
	def heapsize = "heap size "+Runtime.getRuntime().totalMemory()/1000000
}

object Dir
{

	def mkdirs(path: List[String]) = // return true if path was created
		path.tail.foldLeft(new File(path.head)){(a,b) => a.mkdir; new File(a,b)}.mkdir
		
	def mkdir(path: String) = // create single dir
		mkdirs(List(path))

	def getListOfFiles(dir: String):List[File] =
	{
		val d = new File(dir)
		if (d.exists && d.isDirectory)
		{
			d.listFiles.filter(_.isFile).toList
		}
		else
		{
			List[File]()
		}
	}
	
	def getListOfFileNames(dir: String):List[String] =
		for(f<-getListOfFiles(dir)) yield f.getName
		
	def deleteFilesInDir(dir: String)
	{
		for(f<-getListOfFiles(dir)) f.delete
	}

	def saveTxt(name: String,content: String)
	{
		val writer=new PrintWriter(new File(name))
		writer.write(content)
		writer.close()
	}

	def readTxtLines(path:String):Array[String]=
	{
		val timer=new Timer
		println("reading lines of %s , %s".format(path,HeapSize.heapsize))
		val lines=Source.fromFile(path).getLines().toArray
		println("number of lines %d , elapsed %f , %s".format(lines.length,timer.elapsed,HeapSize.heapsize))
		lines
	}

}