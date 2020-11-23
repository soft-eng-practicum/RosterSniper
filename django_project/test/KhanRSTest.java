import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

import java.io.PrintStream;
import java.util.concurrent.TimeUnit;

public class KhanRSTest {
        private static WebDriver driver;
        private final String REGISTER_LINK = "https://tech.rostersniper.com/register/";
        private final String LOGIN_LINK = "https://tech.rostersniper.com/login/";
        private final String LINK = "https://tech.rostersniper.com/";
        private static PrintStream stdOut;


        @BeforeClass
        public static void setUp() {
            System.setProperty("webdriver.chrome.driver", "chromedriver.exe");
            driver = new ChromeDriver();
        }

    /**
     * The following test will test to ensure that users can register without any problems
     */
    @Test
        public void testRegister() {
            driver.get(REGISTER_LINK);
            WebElement email = driver.findElement(By.name("email"));
            WebElement firstName = driver.findElement(By.name("first_name"));
            WebElement password = driver.findElement(By.name("password1"));
            WebElement passwordConfirm = driver.findElement(By.name("password2"));
            WebElement signupButton = driver.findElement(By.cssSelector("body > main > div > div > form > div > button"));

            email.sendKeys("bob789@gmail.com"); //burner email for testing
            firstName.sendKeys("Bobby");
            password.sendKeys("Thedude45"); //password hidden after test for obvious reasons
            passwordConfirm.sendKeys("Thedude45");
            signupButton.click();
            driver.manage().timeouts().implicitlyWait(2, TimeUnit.SECONDS);
            Assert.assertTrue(driver.getPageSource().contains("email_notify"));
        }

    /**
     * The following Selenium test will test the login page to make sure users can login without any problems
     */
    @Test
        public void testLogin() {
        driver.get(LOGIN_LINK);
        WebElement username = driver.findElement(By.name("username"));
        WebElement password = driver.findElement(By.name("password"));

        username.sendKeys("bob234@gmail.com");
        password.sendKeys("Thedude45");
        WebElement login = driver.findElement(By.cssSelector("body > main > div > div > form > div > button"));
        login.click();
        driver.manage().timeouts().implicitlyWait(4, TimeUnit.SECONDS);
        Assert.assertTrue(driver.getPageSource().contains("Apply"));

        }

    /**
     * The following Selenium test will test whether a user can go from the homepage to the Add Courses page
     * without any problem. The automated test will start at the homepage, find a college,
     * and then navigate its way to the Add Courses page for that college.
     */
    @Test
    public void testHomepageToAddCourses() {
        driver.get(LINK);
        WebElement findSchool = driver.findElement(By.linkText("Find Your School"));
        findSchool.click();
        driver.manage().timeouts().implicitlyWait(5, TimeUnit.SECONDS);
        WebElement ggcButton = driver.findElement(By.linkText("Georgia Gwinnett College"));
        ggcButton.click();
        driver.manage().timeouts().implicitlyWait(5, TimeUnit.SECONDS);
        WebElement searchCourses = driver.findElement(By.linkText("Search Courses"));
        searchCourses.click();
        driver.manage().timeouts().implicitlyWait(5, TimeUnit.SECONDS);
        Assert.assertTrue(driver.getPageSource().contains("Apply"));
    }

    @AfterClass
    public static void registerFollowUp() {
        System.setOut(stdOut);
        System.out.println("Test Complete!");
    }



}

